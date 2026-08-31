from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(*roles):
    """Restrict a view to specific User.Role values, and require admin approval
    for roles that need it."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if user.role not in roles:
                messages.error(request, "You do not have permission to view that page.")
                return redirect("core:dashboard")
            if user.needs_approval:
                messages.warning(
                    request,
                    "Your account is awaiting Administrator approval. "
                    "You'll get full access as soon as it's reviewed.",
                )
                return redirect("core:dashboard")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
