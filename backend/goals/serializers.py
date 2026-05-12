from rest_framework import serializers
from .models import SavingsGoal


class SavingsGoalSerializer(serializers.ModelSerializer):
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = SavingsGoal
        fields = ['id', 'name', 'target_amount', 'current_amount', 'deadline', 'percentage', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_percentage(self, obj):
        if not obj.target_amount:
            return 0
        return round(float(obj.current_amount) / float(obj.target_amount) * 100, 1)

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
