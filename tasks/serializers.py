from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status',
            'due_date', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['completed_at', 'created_at', 'updated_at',]

class TaskStatsSerializer(serializers.Serializer):
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    priority_breakdown = serializers.JSONField()