from rest_framework import serializers
from .models import Expense, ExpenseCategory

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name', 'color']

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name',read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'name', 'amount', 'category', 'category_name', 'category_color',
            'transaction_type', 'date', 'description', 'updated_at', 'created_at'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ExpenseStatsSerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    category_breakdown = serializers.JSONField()