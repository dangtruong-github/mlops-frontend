# Generated by Django 4.2 on 2024-05-21 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_movie_price_alter_movie_homepage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='release_date',
            field=models.DateTimeField(),
        ),
    ]