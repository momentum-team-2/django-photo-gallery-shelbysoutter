# Generated by Django 3.0.8 on 2020-08-01 16:48

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0006_auto_20200730_2001'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='favorited_by',
            field=models.ManyToManyField(blank=True, related_name='favorite_album', to=settings.AUTH_USER_MODEL),
        ),
    ]