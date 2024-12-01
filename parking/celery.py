from celery import Celery

app = Celery('ParkingoSistema')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
