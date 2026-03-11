from django.contrib.auth.models import User

def dashboard_admin(request):
    admin = None

    admin_id = request.session.get("dashboard_user_id")
    if admin_id:
        try:
            admin = User.objects.get(id=admin_id)
        except User.DoesNotExist:
            pass

    return {
        "dashboard_admin": admin
    }
