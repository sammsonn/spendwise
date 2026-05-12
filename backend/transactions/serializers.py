from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Currency, Category, Transaction, UserProfile


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'color', 'type']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'amount',
            'description', 'date', 'category', 'category_name', 'category_color',
            'category_icon', 'category_type',
            'is_recurring', 'recurring_interval', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        validated_data['currency'] = profile.preferred_currency
        return super().create(validated_data)

    def validate_category(self, value):
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("Category does not belong to you.")
        return value


class TransactionImportSerializer(serializers.Serializer):
    file = serializers.FileField()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    preferred_currency = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
        source='profile.preferred_currency',
    )
    preferred_currency_code = serializers.CharField(
        source='profile.preferred_currency.code', read_only=True,
    )
    preferred_currency_symbol = serializers.CharField(
        source='profile.preferred_currency.symbol', read_only=True,
    )
    dark_mode = serializers.BooleanField(
        source='profile.dark_mode',
        required=False,
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'preferred_currency', 'preferred_currency_code', 'preferred_currency_symbol',
            'dark_mode',
        ]
        read_only_fields = ['id', 'username']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        instance = super().update(instance, validated_data)
        if profile_data:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            if 'preferred_currency' in profile_data:
                profile.preferred_currency = profile_data['preferred_currency']
            if 'dark_mode' in profile_data:
                profile.dark_mode = profile_data['dark_mode']
            profile.save()
        return instance
