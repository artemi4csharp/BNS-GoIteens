from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    def check_admin(user):
        if user.is_authenticated and user.is_admin():
            return True
        raise PermissionDenied
    return user_passes_test(check_admin)(view_func)

def support_required(view_func):
    def check_support(user):
        if user.is_authenticated and user.is_support():
            return True
        raise PermissionDenied
    return user_passes_test(check_support)(view_func)

def promo_admin_required(view_func):
    def check_promo_admin(user):
        if user.is_authenticated and user.is_promo_admin():
            return True
        raise PermissionDenied
    return user_passes_test(check_promo_admin)(view_func)
