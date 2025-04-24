from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Task, User
from .serializers import TaskSerializer, TaskUpdateSerializer, UserSerializer
from .permissions import IsSuperAdmin, IsAdminOrSuperAdmin, IsOwnerOrReadOnly

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'user':
            return Task.objects.filter(assigned_to=user)
        elif user.role == 'admin':
            return Task.objects.filter(assigned_to__in=User.objects.filter(is_staff=False))
        return Task.objects.all()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.assigned_to:
            return Response({'error': 'Permission denied'}, status=403)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        task = self.get_object()
        if task.status != 'completed':
            return Response({'error': 'Report available only for completed tasks'}, status=400)
        if request.user.role in ['admin', 'superadmin']:
            return Response({
                'completion_report': task.completion_report,
                'worked_hours': task.worked_hours
            })
        return Response({'error': 'Access denied'}, status=403)