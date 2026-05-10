from django.db import models
from django.conf import settings
from transactions.models import Category, Currency


class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='budgets')
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['-year', '-month']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'category', 'month', 'year'],
                name='unique_budget_per_category_month',
            ),
        ]

    def __str__(self):
        return f"{self.category.name} - {self.amount} {self.currency.code} ({self.month}/{self.year})"
