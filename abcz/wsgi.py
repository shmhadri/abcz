"""
WSGI config for abcz project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abcz.settings')

application = get_wsgi_application()


def _env_truthy(name, default="false"):
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _run_startup_migrations_on_render():
    default = os.environ.get("RENDER", "false")
    if not _env_truthy("RUN_MIGRATIONS_ON_STARTUP", default):
        return

    from django.core.management import call_command

    call_command("migrate", interactive=False, verbosity=1)


_run_startup_migrations_on_render()
