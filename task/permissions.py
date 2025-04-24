from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'superadmin'

class IsAdminOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'superadmin']

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.assigned_to == request.user