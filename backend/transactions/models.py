from django.db import models
from django.conf import settings


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)

    class Meta:
        verbose_name_plural = 'currencies'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} ({self.symbol})"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    preferred_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default=1)

    def __str__(self):
        return f"{self.user.username} profile"


class Category(models.Model):
    class Type(models.TextChoices):
        INCOME = 'income', 'Income'
        EXPENSE = 'expense', 'Expense'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, default='')
    color = models.CharField(max_length=7, default='#6366f1')
    type = models.CharField(max_length=7, choices=Type.choices, default=Type.EXPENSE)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_category_per_user'),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transaction(models.Model):
    class RecurringInterval(models.TextChoices):
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='transactions')
    description = models.CharField(max_length=255, blank=True, default='')
    date = models.DateField()
    is_recurring = models.BooleanField(default=False)
    recurring_interval = models.CharField(
        max_length=7,
        choices=RecurringInterval.choices,
        blank=True,
        default='',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.description or 'Transaction'} - {self.amount} {self.currency.code}"
