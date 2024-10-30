from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email,  username, cin, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,  username=username, cin=cin, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, cin, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email,  username, cin, password, **extra_fields)

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    fullname = models.CharField(max_length=50)
    username = models.CharField(max_length=150, unique=True) 
    cin = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    birthdate = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='profile', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    cv_file = models.FileField(upload_to='cv_files/', null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    education = models.TextField(null=True, blank=True)
    languages = models.TextField(null=True, blank=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Avoid clash with auth.User.groups
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  # Avoid clash with auth.User.user_permissions
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [ 'email', 'cin']

    def __str__(self):
        return self.email
