from rest_framework.permissions import BasePermission

from .models import Company


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        company = getattr(user, 'company', None)
        return bool(company and company.role == Company.Role.ADMIN)
