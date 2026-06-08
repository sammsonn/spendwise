from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework.test import APIClient
from decimal import Decimal
from datetime import date
from .models import Budget
from transactions.models import Category, Currency, Transaction, UserProfile


class BudgetModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='test', password='123')
        self.currency = Currency.objects.create(code='RON', symbol='lei', name='Romanian Leu')
        self.category = Category.objects.create(user=self.user, name='Food', type='expense')

    def test_create_budget(self):
        b = Budget.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('500.00'), currency=self.currency,
            month=6, year=2024
        )
        self.assertEqual(b.amount, Decimal('500.00'))
        self.assertEqual(b.month, 6)
        self.assertEqual(b.year, 2024)

    def test_unique_budget_per_category_month(self):
        Budget.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('500'), currency=self.currency,
            month=6, year=2024
        )
        with self.assertRaises(IntegrityError):
            Budget.objects.create(
                user=self.user, category=self.category,
                amount=Decimal('600'), currency=self.currency,
                month=6, year=2024
            )

    def test_same_category_different_months(self):
        Budget.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('500'), currency=self.currency,
            month=5, year=2024
        )
        Budget.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('600'), currency=self.currency,
            month=6, year=2024
        )
        self.assertEqual(Budget.objects.filter(user=self.user).count(), 2)

    def test_budget_ordering(self):
        Budget.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('500'), currency=self.currency,
            month=1, year=2024
        )
        Budget.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('600'), currency=self.currency,
            month=6, year=2025
        )
        budgets = list(Budget.objects.all())
        self.assertGreater(budgets[0].year, budgets[1].year)

    def test_budget_str(self):
        b = Budget.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('500'), currency=self.currency,
            month=6, year=2024
        )
        self.assertIn('Food', str(b))
        self.assertIn('RON', str(b))


class BudgetAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='test', password='testpass123')
        self.currency = Currency.objects.create(code='RON', symbol='lei', name='Romanian Leu')
        UserProfile.objects.create(user=self.user, preferred_currency=self.currency)
        self.category = Category.objects.create(user=self.user, name='Food', type='expense')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_budget_via_api(self):
        response = self.client.post('/api/budgets/', {
            'category': self.category.id,
            'amount': '500.00',
            'month': 6,
            'year': 2024,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Budget.objects.count(), 1)

    def test_budget_spent_calculation(self):
        Budget.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('500'), currency=self.currency,
            month=date.today().month, year=date.today().year
        )
        Transaction.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('150'), currency=self.currency, date=date.today()
        )
        Transaction.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('75'), currency=self.currency, date=date.today()
        )
        response = self.client.get('/api/budgets/')
        self.assertEqual(response.status_code, 200)
        budget_data = response.data['results'][0]
        self.assertEqual(budget_data['spent'], 225.0)

    def test_user_isolation(self):
        User = get_user_model()
        other = User.objects.create_user(username='other', password='pass123')
        Budget.objects.create(
            user=other, category=Category.objects.create(user=other, name='Food', type='expense'),
            amount=Decimal('300'), currency=self.currency,
            month=6, year=2024
        )
        response = self.client.get('/api/budgets/')
        self.assertEqual(response.data['count'], 0)

    def test_cannot_use_other_users_category(self):
        User = get_user_model()
        other = User.objects.create_user(username='other', password='pass123')
        other_cat = Category.objects.create(user=other, name='Stolen', type='expense')
        response = self.client.post('/api/budgets/', {
            'category': other_cat.id,
            'amount': '500.00',
            'month': 6,
            'year': 2024,
        })
        self.assertEqual(response.status_code, 400)
