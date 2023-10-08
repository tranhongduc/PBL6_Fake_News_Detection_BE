from django.db import models

class Account(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, default='Anonymous user')
    email = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=25,default='user')
    status = models.CharField(max_length=25, default='active')
    avatar = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    use_in_migrations = True
