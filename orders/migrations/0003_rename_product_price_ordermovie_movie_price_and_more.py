# Generated by Django 4.2 on 2024-05-21 15:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_ordermovie'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordermovie',
            old_name='product_price',
            new_name='movie_price',
        ),
        migrations.DeleteModel(
            name='OrderProduct',
        ),
    ]
