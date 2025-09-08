from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'  # change to your app name

    def ready(self):
        import inventory.signals  # ensures signal is loaded