from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')  # Đặt giá trị mặc định admin khi createsuperuser
        return self.create_user(email, password, **extra_fields)

class Account(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, default='Anonymous user', unique=False)
    email = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=25, default='user')
    status = models.CharField(max_length=25, default='active')
    avatar = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    use_in_migrations = True

    # Đặt 'email' làm 'USERNAME_FIELD'
    USERNAME_FIELD = 'email'

    # Loại bỏ 'email' khỏi danh sách 'REQUIRED_FIELDS'
    REQUIRED_FIELDS = ['username', 'password']

    objects = CustomAccountManager()

    # Loại bỏ trường 'last_login'
    last_login = None

    # Loại bỏ trường 'is_superuser'
    is_superuser = None
    