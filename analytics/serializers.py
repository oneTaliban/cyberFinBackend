from rest_framework import serializers

class FinancialHealthSerializer(serializers.Serializer):
    savings_rate = serializers.FloatField()
    emergency_fund_months = serializers.FloatField()
    debt_to_income = serializers.FloatField()
    investment_growth = serializers.FloatField()
    overall_score = serializers.FloatField()
    recommendation = serializers.CharField()

class SpendingTrendSerializer(serializers.Serializer):
    month = serializers.CharField()
    income = serializers.DecimalField(max_digits=10, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    savings = serializers.DecimalField(max_digits=10, decimal_places=2)