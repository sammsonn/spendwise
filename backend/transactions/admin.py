from django.contrib import admin
from .models import Currency, Category, Transaction


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'color']
    list_filter = ['type']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'description', 'amount', 'category', 'user']
    list_filter = ['category__type', 'date', 'is_recurring']
    search_fields = ['description']
