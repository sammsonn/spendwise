from rest_framework import serializers
from django.db import models
from .models import Budget
from transactions.models import UserProfile


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    spent = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_name', 'category_color',
            'amount', 'month', 'year', 'spent',
        ]

    def get_spent(self, obj):
        from transactions.models import Transaction
        total = Transaction.objects.filter(
            user=obj.user,
            category=obj.category,
            date__month=obj.month,
            date__year=obj.year,
        ).aggregate(total=models.Sum('amount'))['total']
        return float(total or 0)

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        validated_data['currency'] = profile.preferred_currency
        return super().create(validated_data)

    def validate_category(self, value):
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("Category does not belong to you.")
        return value
