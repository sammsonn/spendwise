from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    CurrencyViewSet, CategoryViewSet, TransactionViewSet,
    RegisterView, ProfileView, stats_summary, stats_by_category,
    stats_balance_trend, stats_monthly_report,
)

router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('stats/summary/', stats_summary, name='stats-summary'),
    path('stats/by-category/', stats_by_category, name='stats-by-category'),
    path('stats/balance-trend/', stats_balance_trend, name='stats-balance-trend'),
    path('stats/monthly-report/', stats_monthly_report, name='stats-monthly-report'),
] + router.urls
