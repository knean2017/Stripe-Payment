"""
Custom middleware to disable CSRF protection completely.
"""
from django.utils.deprecation import MiddlewareMixin


class DisableCSRFMiddleware(MiddlewareMixin):
    """
    Middleware that disables CSRF protection.
    """
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)

