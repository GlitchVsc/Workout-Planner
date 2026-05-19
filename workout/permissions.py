from rest_framework import permissions


class IsPlanOwner(permissions.BasePermission):
    """Allow reads for any object in the queryset; mutations only for the owner."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
