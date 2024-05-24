# Generated by Django 4.2 on 2024-05-22 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0022_actor_slug_movie_slug_variation_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='images',
        ),
        migrations.AddField(
            model_name='movie',
            name='image_urls',
            field=models.URLField(blank=True),
        ),
        migrations.DeleteModel(
            name='Product',
        ),
    ]