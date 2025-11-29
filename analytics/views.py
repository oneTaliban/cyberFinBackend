from django.shortcuts import render
from django.db.models import Sum, Avg
from django.utils import timezone

from datetime import timedelta

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from expenses.models import Expense
from tasks.models import Task

from .serializers import FinancialHealthSerializer, SpendingTrendSerializer

@api_view(['GET'])
def financial_health(request):
    user_expenses = Expense.objects.filter(user=request.user)

    #Calculating core metrics
    total_income = user_expenses.filter(
        transaction_type = 'income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_expenses = user_expenses.filter(
        transaction_type = 'expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    savings = total_income - total_expenses
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0

    #calculating emergency fund 
    monthly_expenses = total_expenses / 12 if total_expenses > 0 else 1
    emergency_fund_months = (savings / monthly_expenses) if monthly_expenses > 0 else 0
    
    #debt to income ration simplified , can come from debt records TODO
    debt_to_income = 12.0

    investment_growth = 7.2 #simplified

    #overall score calculation
    overall_score = min(100,(
        min(savings_rate, 20) + #max 20 points for savings rate
        min(emergency_fund_months * 5, 30) + # max 30 points for emergency fund
        max(0, 30 - (debt_to_income * 2)) + # max 30 points for low debt-to-income
        min(investment_growth, 20) # max 20 points for investment growth
    ))

    #Recommendation generation
    if savings_rate < 10:
        recommedation = "Focus on increasing your savings rate. Aim for at least 20%."
    elif emergency_fund_months < 3:
        recommedation = "Build you emergency fund to to cover 3-6 months of expenses."
    elif debt_to_income > 20:
        recommedation = "Consider strategies to reduce your debt to income ratio."
    else:
        recommedation = "You are doing great! Consider increasing investment contributions."

    data = {
        'savings_rate': round(savings_rate, 1),
        'emergency_fund_months': round(emergency_fund_months, 1),
        'debt_to_income': debt_to_income,
        'investment_growth': investment_growth,
        'overall_score': round(overall_score),
        'recommendation': recommedation,
    }

    serializer = FinancialHealthSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
def spending_trends(request):
    trends = []
    for i in range(6):
        month = timezone.now() - timedelta(days=30 * (5 - i))
        month_str = month.strftime('%Y-%m')

        monthly_income = Expense.objects.filter(
            user= request.user,
            transaction_type = 'income',
            date__year = month.year,
            date__month = month.month,
        ).aggregate(total=Sum('amount'))['total'] or 0

        monthly_expenses = Expense.objects.filter(
            user  = request.user,
            transaction_type = 'expense',
            date__year = month.year,
            date__month = month.month,
        ).aggregate(total=Sum('amount'))['total'] or 0

        trends.append({
            'month': month_str,
            'income': float(monthly_income),
            'expenses': float(monthly_expenses),
            'savings': float(monthly_income - monthly_expenses),
        })

    serializer = SpendingTrendSerializer(trends, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def productivity_metrics(request):
    user_tasks = Task.objects.filter(user=request.user)

    #calculating productivity metrics
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(status='completed').count()
    
    #Focus time calculation -simplified -- come from time tracking
    focus_time_minutes = 165 #minutes

    #Efficiency calculation
    efficiency = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Weekly Goal progress
    weekly_goal_progress = 65  #simplified

    data = {
        'focus_time': focus_time_minutes,
        'tasks_completed': completed_tasks,
        'total_tasks': total_tasks,
        'efficiency': round(efficiency, 1),
        'weakly_goal_progress': weekly_goal_progress,
        'productivity_tip': "Try the Pomodoro technique: 25 minutes focussed work, 5 minutes break.",
    }
    
    return Response(data)

@api_view(['GET'])
def budget_recommendations(request):
    user_expenses = Expense.objects.filter(user=request.user)

    #Getting the current month expenses by category
    current_month = timezone.now()
    category_spending = user_expenses.filter(
        transaction_type = 'expense',
        date__year = current_month.year,
        date__month = current_month.month,
    ).values('category__name').annotate(
        total_spent = Sum('amount')
    )

    #Ideal budget allocations (simplified)
    ideal_allocations = {
        "Food": 0.15, #15% of income
        "Transportation": 0.10,
        "Utilities": 0.08,
        "Entertainment": 0.05,
        "Healthcare": 0.08,
        "Other": 0.04,
    }

    total_income = user_expenses.filter(
        transaction_type='income',
        date__year = current_month.year,
        date__month = current_month.month,
    ).annotate(total=Sum('amount'))['total'] or 1

    recommendation = []

    for category in category_spending:
        category_name = category['category__name']
        spent = abs(category['total_spent'])
        ideal = total_income * ideal_allocations.get(category_name, 0.05)

        if spent > ideal * 1.1: # 10% over budget
            recommendation.append({
                'category': category_name,
                'message': f'You\'re spending ${spent-ideal:.2f} over budget in {category_name}. Consider reducing expenses.',
                'severity': 'high',
            })
        elif spent < ideal * 0.8: #20% under budget
            recommendation.append({
                'category': category_name,
                'message': f'You have ${ideal - spent:.2f} unused in your {category_name} budget. Consider reallocating to savings',
                'severity': 'low',
            })
        
        return Response({
            'recommendation': recommendation,
            'total_income': float(total_income),
            'analysis_date': current_month.isoformat()
        })