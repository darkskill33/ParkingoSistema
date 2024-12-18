# Generated by Django 5.1.3 on 2024-11-24 08:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0003_remove_reservation_start_date_reservation_end_time_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='parkingspot',
            name='daily_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='parkingspot',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='parkingspot',
            name='is_rentable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='parkingspot',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_spots', to=settings.AUTH_USER_MODEL),
        ),
    ]
