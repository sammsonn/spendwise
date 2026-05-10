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
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if category_type:
            qs = qs.filter(category__type=category_type)
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


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        UserProfile.objects.get_or_create(user=self.request.user)
        return self.request.user
