from django.apps import AppConfig


class PhonicsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phonics'

    def ready(self):
        import phonics.signals  # noqa: F401
