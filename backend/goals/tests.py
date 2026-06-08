from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from decimal import Decimal
from datetime import date
from .models import SavingsGoal


class SavingsGoalModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='test', password='123')

    def test_create_goal(self):
        g = SavingsGoal.objects.create(
            user=self.user, name='Vacation',
            target_amount=Decimal('2000.00'), current_amount=Decimal('500.00'),
            deadline=date(2025, 8, 1)
        )
        self.assertEqual(g.name, 'Vacation')
        self.assertEqual(g.target_amount, Decimal('2000.00'))
        self.assertEqual(g.current_amount, Decimal('500.00'))

    def test_goal_default_current_amount(self):
        g = SavingsGoal.objects.create(
            user=self.user, name='New Laptop',
            target_amount=Decimal('5000.00')
        )
        self.assertEqual(g.current_amount, Decimal('0'))

    def test_goal_without_deadline(self):
        g = SavingsGoal.objects.create(
            user=self.user, name='Emergency Fund',
            target_amount=Decimal('10000.00')
        )
        self.assertIsNone(g.deadline)

    def test_goal_str(self):
        g = SavingsGoal.objects.create(
            user=self.user, name='Car',
            target_amount=Decimal('15000'), current_amount=Decimal('3000')
        )
        self.assertIn('Car', str(g))
        self.assertIn('3000', str(g))
        self.assertIn('15000', str(g))

    def test_goal_ordering(self):
        SavingsGoal.objects.create(
            user=self.user, name='First', target_amount=Decimal('1000')
        )
        SavingsGoal.objects.create(
            user=self.user, name='Second', target_amount=Decimal('2000')
        )
        goals = list(SavingsGoal.objects.all())
        self.assertEqual(goals[0].name, 'Second')


class SavingsGoalAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='test', password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_goal_via_api(self):
        response = self.client.post('/api/goals/', {
            'name': 'Vacation',
            'target_amount': '2000.00',
            'current_amount': '0',
            'deadline': '2025-08-01',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SavingsGoal.objects.count(), 1)

    def test_percentage_calculation(self):
        SavingsGoal.objects.create(
            user=self.user, name='Test',
            target_amount=Decimal('1000'), current_amount=Decimal('250')
        )
        response = self.client.get('/api/goals/')
        goal_data = response.data['results'][0]
        self.assertEqual(goal_data['percentage'], 25.0)

    def test_percentage_zero_target(self):
        SavingsGoal.objects.create(
            user=self.user, name='Empty',
            target_amount=Decimal('0'), current_amount=Decimal('0')
        )
        response = self.client.get('/api/goals/')
        goal_data = response.data['results'][0]
        self.assertEqual(goal_data['percentage'], 0)

    def test_update_goal(self):
        g = SavingsGoal.objects.create(
            user=self.user, name='Fund',
            target_amount=Decimal('5000'), current_amount=Decimal('1000')
        )
        response = self.client.patch(f'/api/goals/{g.id}/', {
            'current_amount': '2500.00',
        })
        self.assertEqual(response.status_code, 200)
        g.refresh_from_db()
        self.assertEqual(g.current_amount, Decimal('2500.00'))

    def test_delete_goal(self):
        g = SavingsGoal.objects.create(
            user=self.user, name='Delete Me',
            target_amount=Decimal('1000')
        )
        response = self.client.delete(f'/api/goals/{g.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(SavingsGoal.objects.count(), 0)

    def test_user_isolation(self):
        User = get_user_model()
        other = User.objects.create_user(username='other', password='pass123')
        SavingsGoal.objects.create(
            user=other, name='Secret Goal',
            target_amount=Decimal('9999')
        )
        response = self.client.get('/api/goals/')
        self.assertEqual(response.data['count'], 0)

    def test_cannot_access_other_users_goal(self):
        User = get_user_model()
        other = User.objects.create_user(username='other', password='pass123')
        g = SavingsGoal.objects.create(
            user=other, name='Private',
            target_amount=Decimal('5000')
        )
        response = self.client.get(f'/api/goals/{g.id}/')
        self.assertEqual(response.status_code, 404)
