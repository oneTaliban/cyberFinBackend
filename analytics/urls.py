from django.urls import path
from .views import financial_health, spending_trends, productivity_metrics, budget_recommendations

urlpatterns = [
    path('financial-health/', financial_health, name='financial_health'),
    path('spending-trends/', spending_trends, name='spending_trends'),
    path('productivity-metrics/', productivity_metrics, name='productivity_metrics'),
    path('budget_recommendations/', budget_recommendations, name='budget_recommendations'),
]