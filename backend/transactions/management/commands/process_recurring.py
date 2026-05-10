from datetime import date, timedelta
from django.core.management.base import BaseCommand
from transactions.models import Transaction


class Command(BaseCommand):
    help = 'Generate transactions from recurring templates'

    def handle(self, *args, **options):
        today = date.today()
        recurring = Transaction.objects.filter(is_recurring=True).select_related('category')
        created = 0

        for template in recurring:
            last = Transaction.objects.filter(
                user=template.user,
                category=template.category,
                amount=template.amount,
                is_recurring=False,
                description=template.description,
            ).order_by('-date').first()

            last_date = last.date if last else template.date
            next_date = self._next_date(last_date, template.recurring_interval)

            while next_date <= today:
                Transaction.objects.create(
                    user=template.user,
                    category=template.category,
                    amount=template.amount,
                    currency=template.currency,
                    description=template.description,
                    date=next_date,
                    is_recurring=False,
                )
                created += 1
                next_date = self._next_date(next_date, template.recurring_interval)

        self.stdout.write(self.style.SUCCESS(f'Created {created} recurring transactions'))

    def _next_date(self, current, interval):
        if interval == 'daily':
            return current + timedelta(days=1)
        elif interval == 'weekly':
            return current + timedelta(weeks=1)
        elif interval == 'monthly':
            month = current.month + 1
            year = current.year
            if month > 12:
                month = 1
                year += 1
            day = min(current.day, 28)
            return current.replace(year=year, month=month, day=day)
        return current + timedelta(days=1)
