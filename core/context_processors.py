def role_flags(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}
    from accounts.models import User

    return {
        "is_patient": user.role == User.Role.PATIENT,
        "is_doctor": user.role == User.Role.DOCTOR,
        "is_admin_role": user.role == User.Role.ADMINISTRATOR,
        "is_emergency": user.role == User.Role.EMERGENCY,
        "is_department": user.role == User.Role.DEPARTMENT,
        "needs_approval": user.needs_approval,
    }
