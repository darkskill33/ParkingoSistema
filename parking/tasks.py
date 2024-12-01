from celery import shared_task
from .views import free_expired_spots

@shared_task
def check_for_expired_reservations():
    free_expired_spots()
