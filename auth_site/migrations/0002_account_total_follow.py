# Generated by Django 4.1.12 on 2023-11-21 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_site', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='total_follow',
            field=models.IntegerField(default=0),
        ),
    ]
