# Generated by Django 4.2 on 2024-05-21 04:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_actor_short_name_2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='actor',
            name='short_name_2',
        ),
    ]