from django.conf import settings


def authentication_options(request):
    """Expose enabled sign-in providers to every authentication surface."""
    return {"google_login_enabled": settings.GOOGLE_LOGIN_ENABLED}
