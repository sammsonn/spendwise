from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework.test import APIClient
from decimal import Decimal
from datetime import date
from .models import Transaction, Category, Currency, UserProfile


class TransactionModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='test', password='123')
        self.currency = Currency.objects.create(code='RON', symbol='lei', name='Romanian Leu')
        self.category = Category.objects.create(
            user=self.user, name='Food', type='expense'
        )

    def test_create_transaction(self):
        t = Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('150.50'),
            currency=self.currency,
            date=date.today(),
            description='Lunch'
        )
        self.assertEqual(t.amount, Decimal('150.50'))
        self.assertTrue(Transaction.objects.filter(description='Lunch').exists())

    def test_transaction_without_category(self):
        t = Transaction.objects.create(
            user=self.user,
            category=None,
            amount=Decimal('50.00'),
            currency=self.currency,
            date=date.today(),
        )
        self.assertIsNone(t.category)

    def test_transaction_ordering(self):
        Transaction.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('10'), currency=self.currency, date=date(2024, 1, 1)
        )
        Transaction.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('20'), currency=self.currency, date=date(2024, 6, 1)
        )
        transactions = list(Transaction.objects.all())
        self.assertGreater(transactions[0].date, transactions[1].date)

    def test_recurring_transaction(self):
        t = Transaction.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('100'), currency=self.currency,
            date=date.today(), is_recurring=True, recurring_interval='monthly'
        )
        self.assertTrue(t.is_recurring)
        self.assertEqual(t.recurring_interval, 'monthly')

    def test_transaction_str(self):
        t = Transaction.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('75.00'), currency=self.currency,
            date=date.today(), description='Groceries'
        )
        self.assertIn('Groceries', str(t))
        self.assertIn('RON', str(t))


class CategoryModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='test', password='123')

    def test_create_category(self):
        c = Category.objects.create(user=self.user, name='Transport', type='expense')
        self.assertEqual(c.name, 'Transport')
        self.assertEqual(c.type, 'expense')
        self.assertEqual(c.color, '#6366f1')

    def test_unique_category_per_user(self):
        Category.objects.create(user=self.user, name='Food', type='expense')
        with self.assertRaises(IntegrityError):
            Category.objects.create(user=self.user, name='Food', type='expense')

    def test_same_name_different_users(self):
        User = get_user_model()
        user2 = User.objects.create_user(username='test2', password='123')
        Category.objects.create(user=self.user, name='Food', type='expense')
        Category.objects.create(user=user2, name='Food', type='expense')
        self.assertEqual(Category.objects.filter(name='Food').count(), 2)

    def test_category_ordering(self):
        Category.objects.create(user=self.user, name='Zebra', type='expense')
        Category.objects.create(user=self.user, name='Alpha', type='income')
        categories = list(Category.objects.filter(user=self.user))
        self.assertEqual(categories[0].name, 'Alpha')


class TransactionAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='test', password='testpass123')
        self.currency = Currency.objects.create(code='RON', symbol='lei', name='Romanian Leu')
        UserProfile.objects.create(user=self.user, preferred_currency=self.currency)
        self.category = Category.objects.create(user=self.user, name='Food', type='expense')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_transactions(self):
        Transaction.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('50'), currency=self.currency, date=date.today()
        )
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_create_transaction_via_api(self):
        response = self.client.post('/api/transactions/', {
            'amount': '99.99',
            'category': self.category.id,
            'date': '2024-06-01',
            'description': 'Test meal',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_filter_by_category(self):
        cat2 = Category.objects.create(user=self.user, name='Transport', type='expense')
        Transaction.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('10'), currency=self.currency, date=date.today()
        )
        Transaction.objects.create(
            user=self.user, category=cat2,
            amount=Decimal('20'), currency=self.currency, date=date.today()
        )
        response = self.client.get(f'/api/transactions/?category={self.category.id}')
        self.assertEqual(response.data['count'], 1)

    def test_user_isolation(self):
        User = get_user_model()
        other = User.objects.create_user(username='other', password='pass123')
        Transaction.objects.create(
            user=other, category=None,
            amount=Decimal('100'), currency=self.currency, date=date.today()
        )
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.data['count'], 0)

    def test_stats_summary(self):
        income_cat = Category.objects.create(user=self.user, name='Salary', type='income')
        Transaction.objects.create(
            user=self.user, category=income_cat,
            amount=Decimal('5000'), currency=self.currency, date=date.today()
        )
        Transaction.objects.create(
            user=self.user, category=self.category,
            amount=Decimal('200'), currency=self.currency, date=date.today()
        )
        today = date.today()
        response = self.client.get(f'/api/stats/summary/?month={today.month}&year={today.year}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['income'], 5000.0)
        self.assertEqual(response.data['expenses'], 200.0)
        self.assertEqual(response.data['balance'], 4800.0)
