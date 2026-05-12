import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.db.models import Sum, Q
from django.http import HttpResponse
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from .models import Currency, Category, Transaction, UserProfile
from .serializers import (
    CurrencySerializer, CategorySerializer, TransactionSerializer,
    TransactionImportSerializer, RegisterSerializer, UserProfileSerializer,
)


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'is_recurring']
    search_fields = ['description']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user).select_related('category')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        category_type = self.request.query_params.get('type')
        amount_min = self.request.query_params.get('amount_min')
        amount_max = self.request.query_params.get('amount_max')
        categories = self.request.query_params.get('categories')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if category_type:
            qs = qs.filter(category__type=category_type)
        if amount_min:
            qs = qs.filter(amount__gte=amount_min)
        if amount_max:
            qs = qs.filter(amount__lte=amount_max)
        if categories:
            cat_ids = [int(c) for c in categories.split(',') if c.strip().isdigit()]
            if cat_ids:
                qs = qs.filter(category_id__in=cat_ids)
        return qs

    @action(detail=False, methods=['post'], url_path='import-csv')
    def import_csv(self, request):
        serializer = TransactionImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']

        try:
            decoded = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return Response({"error": "File must be UTF-8 encoded CSV."}, status=400)

        reader = csv.DictReader(io.StringIO(decoded))
        required = {'amount', 'date', 'category'}
        if not required.issubset(set(reader.fieldnames or [])):
            return Response(
                {"error": f"CSV must contain columns: {', '.join(sorted(required))}"},
                status=400,
            )

        created = 0
        errors = []
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_currency = profile.preferred_currency
        for i, row in enumerate(reader, start=2):
            try:
                category = Category.objects.get(user=request.user, name=row['category'])
                amount = Decimal(row['amount'])
                date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                Transaction.objects.create(
                    user=request.user,
                    category=category,
                    currency=user_currency,
                    amount=amount,
                    date=date,
                    description=row.get('description', ''),
                )
                created += 1
            except (Category.DoesNotExist, InvalidOperation, ValueError) as e:
                errors.append(f"Row {i}: {str(e)}")

        return Response({"created": created, "errors": errors})

    @action(detail=False, methods=['get'], url_path='export-csv')
    def export_csv(self, request):
        qs = self.get_queryset()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
        writer = csv.writer(response)
        writer.writerow(['date', 'category', 'type', 'amount', 'description'])
        for t in qs:
            writer.writerow([
                t.date, t.category.name if t.category else '',
                t.category.type if t.category else '', t.amount,
                t.description,
            ])
        return response

    @action(detail=False, methods=['get'], url_path='export-pdf')
    def export_pdf(self, request):
        qs = self.get_queryset()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'

        doc = SimpleDocTemplate(response, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("SpendWise - Transaction Report", styles['Title']))
        elements.append(Spacer(1, 0.5 * cm))

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        currency_code = profile.preferred_currency.code

        data = [['Date', 'Category', 'Type', f'Amount ({currency_code})', 'Description']]
        for t in qs:
            data.append([
                str(t.date),
                t.category.name if t.category else '',
                t.category.type if t.category else '',
                str(t.amount),
                t.description[:40],
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ]))
        elements.append(table)
        doc.build(elements)
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_summary(request):
    month = request.query_params.get('month')
    year = request.query_params.get('year')
    qs = Transaction.objects.filter(user=request.user)
    if month and year:
        qs = qs.filter(date__month=month, date__year=year)
    income = qs.filter(category__type='income').aggregate(total=Sum('amount'))['total'] or 0
    expenses = qs.filter(category__type='expense').aggregate(total=Sum('amount'))['total'] or 0
    return Response({
        'income': float(income),
        'expenses': float(expenses),
        'balance': float(income - expenses),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_by_category(request):
    month = request.query_params.get('month')
    year = request.query_params.get('year')
    category_type = request.query_params.get('type', 'expense')
    qs = Transaction.objects.filter(user=request.user, category__type=category_type)
    if month and year:
        qs = qs.filter(date__month=month, date__year=year)
    data = qs.values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')
    return Response([
        {'category': item['category__name'], 'color': item['category__color'], 'total': float(item['total'])}
        for item in data
    ])


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_balance_trend(request):
    month = int(request.query_params.get('month', datetime.now().month))
    year = int(request.query_params.get('year', datetime.now().year))
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    results = []
    for i in range(5, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        qs = Transaction.objects.filter(user=request.user, date__month=m, date__year=y)
        inc = qs.filter(category__type='income').aggregate(total=Sum('amount'))['total'] or 0
        exp = qs.filter(category__type='expense').aggregate(total=Sum('amount'))['total'] or 0
        results.append({
            'label': f'{month_names[m - 1]} {y}',
            'balance': float(inc - exp),
        })
    cumulative = []
    running = 0
    for r in results:
        running += r['balance']
        cumulative.append({'label': r['label'], 'balance': round(running, 2)})
    return Response(cumulative)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_monthly_report(request):
    month = int(request.query_params.get('month', datetime.now().month))
    year = int(request.query_params.get('year', datetime.now().year))

    prev_month = month - 1
    prev_year = year
    if prev_month <= 0:
        prev_month += 12
        prev_year -= 1

    qs_current = Transaction.objects.filter(user=request.user, date__month=month, date__year=year)
    qs_prev = Transaction.objects.filter(user=request.user, date__month=prev_month, date__year=prev_year)

    curr_income = float(qs_current.filter(category__type='income').aggregate(total=Sum('amount'))['total'] or 0)
    curr_expenses = float(qs_current.filter(category__type='expense').aggregate(total=Sum('amount'))['total'] or 0)
    prev_income = float(qs_prev.filter(category__type='income').aggregate(total=Sum('amount'))['total'] or 0)
    prev_expenses = float(qs_prev.filter(category__type='expense').aggregate(total=Sum('amount'))['total'] or 0)

    def pct_change(curr, prev):
        if prev == 0:
            return 100.0 if curr > 0 else 0.0
        return round((curr - prev) / prev * 100, 1)

    top_categories = list(
        qs_current.filter(category__type='expense')
        .values('category__id', 'category__name', 'category__color')
        .annotate(total=Sum('amount'))
        .order_by('-total')[:5]
    )

    from budgets.models import Budget
    budgets = Budget.objects.filter(user=request.user, month=month, year=year).select_related('category')
    budget_adherence = []
    for b in budgets:
        spent = float(
            qs_current.filter(category=b.category).aggregate(total=Sum('amount'))['total'] or 0
        )
        budget_adherence.append({
            'category': b.category.name,
            'category_color': b.category.color,
            'budgeted': float(b.amount),
            'spent': spent,
            'percentage': round(spent / float(b.amount) * 100, 1) if float(b.amount) else 0,
        })

    return Response({
        'current': {
            'income': curr_income,
            'expenses': curr_expenses,
            'balance': curr_income - curr_expenses,
        },
        'previous': {
            'income': prev_income,
            'expenses': prev_expenses,
            'balance': prev_income - prev_expenses,
        },
        'changes': {
            'income': pct_change(curr_income, prev_income),
            'expenses': pct_change(curr_expenses, prev_expenses),
            'balance': pct_change(curr_income - curr_expenses, prev_income - prev_expenses),
        },
        'top_categories': [
            {
                'id': c['category__id'],
                'name': c['category__name'],
                'color': c['category__color'],
                'total': float(c['total']),
            }
            for c in top_categories
        ],
        'budget_adherence': budget_adherence,
    })


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        UserProfile.objects.get_or_create(user=self.request.user)
        return self.request.user
