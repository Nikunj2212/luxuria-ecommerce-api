from django.shortcuts import redirect
from django.urls import reverse

def dashboard_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("dashboard_user_id"):
            return redirect("dashboard:dashboard_login")
        return view_func(request, *args, **kwargs)
    return wrapper
