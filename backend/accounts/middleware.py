from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import reverse

class AdminAccessMiddleware:
    """Restricts access to Django Admin to staff users and emails listed in ADMIN_EMAILS."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            user = request.user
            if user.is_authenticated:
                admin_emails = getattr(settings, 'ADMIN_EMAILS', [])
                if admin_emails:
                    if user.email not in admin_emails and not user.is_superuser:
                        raise PermissionDenied("Access to Admin Panel is restricted to authorized admin emails.")
        response = self.get_response(request)
        return response
