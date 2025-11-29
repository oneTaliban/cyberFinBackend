from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import Sum, Count
from django.utils import timezone

from .models import Expense, ExpenseCategory
from .serializers import ExpenseSerializer, ExpenseCategorySerializer,  ExpenseStatsSerializer

class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseCategorySerializer

    def get_queryset(self):
        return ExpenseCategory.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExpenseViewset(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        user_expenses = self.get_queryset()

        #calculating totals
        total_income = user_expenses.filter(
            transaction_type = 'income'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_expenses = user_expenses.filter(
            transaction_type = 'expense'
        ).aggregate(total=Sum('amount'))['total'] or 0

        balance = total_income - total_expenses

        #Category breakdown
        category_breakdown = user_expenses.filter(
            transaction_type='expenses'
        ).values(
            'category__name','category__color'
        ).annotate(
            total = Sum('amount'),
            count=Count('id')
        ).order_by('-total')

        data = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': balance,
            'category_breakdown': list(category_breakdown)
        }

        serializer =  ExpenseStatsSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def monthly_summary(self, request):
        from django.db.models.functions import TruncMonth
        from django.db.models import Q

        monthly_data = self.get_queryset().annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            income=Sum('amount', filter=Q(transaction_type='income')),
            expenses = Sum('amount', filter=Q(transaction_type='expense'))
        ).order_by('month')

        return Response(list(monthly_data))
        
        

