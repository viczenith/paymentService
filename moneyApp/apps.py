from django.apps import AppConfig


class MoneyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'moneyApp'

    def ready(self):
        import moneyApp.signals
