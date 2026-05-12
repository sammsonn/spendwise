from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SavingsGoalViewSet

router = DefaultRouter()
router.register(r'goals', SavingsGoalViewSet, basename='goal')

urlpatterns = router.urls
