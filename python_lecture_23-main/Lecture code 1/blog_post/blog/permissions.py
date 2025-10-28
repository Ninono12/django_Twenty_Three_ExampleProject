from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(obj.owner == request.user)


class ReadOnlyOrAdminOrOwner(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'POST', 'HEAD', 'OPTIONS'):
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return bool(obj.owner == request.user) or request.user.is_staff
