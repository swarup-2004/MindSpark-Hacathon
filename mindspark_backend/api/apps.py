from django.apps import AppConfig

from datetime import timedelta
from django.db.models.signals import post_migrate

class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        # Import the Celery app

        post_migrate.connect(my_post_migrate_handler)

        
def my_post_migrate_handler(sender, **kwargs):
    from django_celery_beat.models import PeriodicTask, IntervalSchedule
    from .tasks import fetch_and_store_articles

    # Check if the interval schedule already exists (for a daily job)
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=1,  # Number of days
        period=IntervalSchedule.DAYS,  # Period type
    )

    # Check if the task already exists to avoid duplicating it
    if not PeriodicTask.objects.filter(name="Fetch Defense And Geopolitical Articles Daily").exists():
        PeriodicTask.objects.create(
            interval=schedule,  # Use the schedule we created
            name="Fetch Defense And Geopolitical Articles Daily",  # Task name
            task="api.tasks.fetch_and_store_articles",  # The task to execute
            args="['defense', 'military', 'security', 'geopolitics']",  # Task arguments
        )
