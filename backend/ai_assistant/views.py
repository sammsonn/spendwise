from datetime import datetime
from decimal import Decimal

from django.db.models import Sum, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from transactions.models import Category, Transaction
from budgets.models import Budget
from goals.models import SavingsGoal
from .gemini import generate


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_categorize(request):
    description = (request.data.get('description') or '').strip()
    if not description:
        return Response({'category_id': None})

    categories = Category.objects.filter(user=request.user)
    if not categories.exists():
        return Response({'category_id': None})

    cat_list = ', '.join(f'{c.id}:{c.name} ({c.type})' for c in categories)
    prompt = (
        f"Given these transaction categories: [{cat_list}], "
        f"which category best matches this transaction description: '{description}'? "
        f"Respond with ONLY the category ID number, nothing else."
    )

    try:
        result = generate(prompt)
        category_id = int(result.strip())
        if not categories.filter(id=category_id).exists():
            return Response({'category_id': None})
        return Response({'category_id': category_id})
    except Exception:
        return Response({'category_id': None})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    message = (request.data.get('message') or '').strip()
    if not message:
        return Response({'reply': 'Please enter a message.'}, status=400)

    try:
        context = _build_financial_context(request.user)
        prompt = (
            "You are a helpful financial assistant for SpendWise, a personal finance app. "
            "Answer questions about the user's personal finances based on their data below. "
            "Be concise, specific, and use actual numbers from their data. "
            "Format currency amounts with two decimal places. "
            "If the data doesn't contain enough information to answer, say so honestly.\n\n"
            f"{context}\n\n"
            f"User's question: {message}"
        )
        reply = generate(prompt)
        return Response({'reply': reply})
    except Exception:
        return Response({'reply': 'Sorry, I\'m unable to process your request right now. Please try again later.'})


def _build_financial_context(user):
    now = datetime.now()
    month, year = now.month, now.year
    sections = []

    transactions = (
        Transaction.objects.filter(user=user)
        .select_related('category')
        .order_by('-date')[:50]
    )
    if transactions:
        lines = []
        for t in transactions:
            cat = t.category.name if t.category else 'Uncategorized'
            cat_type = t.category.type if t.category else 'unknown'
            lines.append(f"  {t.date} | {t.description or 'No description'} | {t.amount} | {cat} ({cat_type})")
        sections.append("RECENT TRANSACTIONS (last 50):\n" + '\n'.join(lines))

    qs = Transaction.objects.filter(user=user, date__month=month, date__year=year)
    income = qs.filter(category__type='income').aggregate(t=Sum('amount'))['t'] or Decimal('0')
    expenses = qs.filter(category__type='expense').aggregate(t=Sum('amount'))['t'] or Decimal('0')
    sections.append(
        f"CURRENT MONTH SUMMARY ({now.strftime('%B %Y')}):\n"
        f"  Income: {income:.2f}, Expenses: {expenses:.2f}, Balance: {income - expenses:.2f}"
    )

    by_cat = (
        qs.filter(category__type='expense')
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    if by_cat:
        lines = [f"  {item['category__name']}: {item['total']:.2f}" for item in by_cat]
        sections.append("SPENDING BY CATEGORY (this month):\n" + '\n'.join(lines))

    budgets = Budget.objects.filter(user=user, month=month, year=year).select_related('category')
    if budgets:
        lines = []
        for b in budgets:
            spent = qs.filter(category=b.category).aggregate(t=Sum('amount'))['t'] or Decimal('0')
            lines.append(f"  {b.category.name}: budget {b.amount:.2f}, spent {spent:.2f}")
        sections.append("BUDGETS (this month):\n" + '\n'.join(lines))

    goals = SavingsGoal.objects.filter(user=user)
    if goals:
        lines = []
        for g in goals:
            pct = (g.current_amount / g.target_amount * 100) if g.target_amount else 0
            deadline = g.deadline.isoformat() if g.deadline else 'No deadline'
            lines.append(f"  {g.name}: {g.current_amount:.2f}/{g.target_amount:.2f} ({pct:.0f}%), deadline: {deadline}")
        sections.append("SAVINGS GOALS:\n" + '\n'.join(lines))

    return '\n\n'.join(sections)
