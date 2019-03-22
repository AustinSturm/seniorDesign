from rest_framework import permissions

class IsDeviceOwner(permissions.BasePermission):
    # defined on requests
    def has_permission(self, request, view):
        return True

    # defined on gets
    def has_object_permission(self, request, view, obj):
        return True
