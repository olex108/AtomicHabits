from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Разрешение: доступ к объекту имеет только его создатель.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
