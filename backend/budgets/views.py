from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Budget
from .serializers import BudgetSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['month', 'year', 'category']

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related('category')
