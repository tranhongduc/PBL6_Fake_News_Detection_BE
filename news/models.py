from django.db import models
from django.urls import reverse
from auth_site.models import Account

class Categories(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    use_in_migrations = True
    
class News(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=512)
    text = models.TextField(db_collation='utf8mb4_unicode_ci')
    image = models.CharField(max_length=255, blank=True, null=True)
    label = models.CharField(max_length=10, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    use_in_migrations = True

class Comments(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    use_in_migrations = True

class Interacts(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=10)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    target_type = models.CharField(max_length=10)
    target_id = models.IntegerField()
    use_in_migration = True
    
