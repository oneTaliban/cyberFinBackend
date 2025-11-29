from django.db import models
from django.contrib.auth.models import User

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#00ff00')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['name', 'user']

    def __str__(self): 
        return self.name

class Expense(models.Model):
    TRANSACTION_TYPES = [  
        ('income', "Income"),
        ('expense', "Expense"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name =  models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='expense')
    date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        ordering = ['-date', '-created_at']

    def __str__(self): 
        return f"{self.name} - {self.amount}"