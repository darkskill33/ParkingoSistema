# Generated by Django 5.1.3 on 2024-11-10 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=25)),
                ('password', models.CharField(max_length=25)),
                ('name', models.CharField(max_length=25)),
                ('lastname', models.CharField(max_length=25)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
            ],
        ),
    ]
