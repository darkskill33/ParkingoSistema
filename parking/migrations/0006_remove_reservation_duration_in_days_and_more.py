# Generated by Django 5.1.3 on 2024-11-24 16:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0005_reservation_is_paid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='duration_in_days',
        ),
        migrations.AlterField(
            model_name='reservation',
            name='spot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='parking.parkingspot'),
        ),
    ]