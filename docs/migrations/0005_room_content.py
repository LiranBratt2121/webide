# Generated by Django 4.2 on 2023-05-17 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0004_room_slug_alter_room_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='content',
            field=models.TextField(blank=True),
        ),
    ]