from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Products'

    # def ready(self):
    #     import Products.signals  # signals.py faylni import qilish