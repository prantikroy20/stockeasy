from django.apps import AppConfig


class MedicinesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medicines'
    
    def ready(self):
        # Import the templatetags module to ensure it's loaded
        import medicines.templatetags.medicine_filters