# Generated by Django 4.1.12 on 2023-11-21 16:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comments',
            name='total_like',
        ),
        migrations.RemoveField(
            model_name='news',
            name='total_like',
        ),
        migrations.RemoveField(
            model_name='news',
            name='total_save',
        ),
        migrations.RemoveField(
            model_name='news',
            name='total_view',
        ),
    ]
