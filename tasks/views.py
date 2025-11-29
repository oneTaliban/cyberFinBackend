from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django.db.models import Q, Count
from django.utils import timezone

from .models import Task
from .serializers import TaskSerializer, TaskStatsSerializer

class TaskViewset(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['POST'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        return Response(TaskSerializer(task).data)
    
    @action(detail=False, methods=['GET'])
    def stats(self, request):
        user_tasks = self.get_queryset()

        total_tasks = user_tasks.count()
        completed_tasks = user_tasks.filter(status='completed').count()
        pending_tasks = user_tasks.filter(status='pending').count()
        completion_rate = (completed_tasks / total_tasks * 100 ) if total_tasks > 0 else 0

        priority_breakdown = user_tasks.values('priority').annotate(
            count=Count('id')
        ).order_by('prority')

        data = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'completion_rate': completion_rate,
            'priority_breakdown': list(priority_breakdown),
        }

        serializer = TaskStatsSerializer(data)
        return Response(serializer.data)
