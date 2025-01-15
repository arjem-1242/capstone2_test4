from django.contrib.auth.models import UserManager  # For creating custom user managers
from django.contrib.auth.base_user import AbstractBaseUser  # For the base user class
from django.utils import timezone  # For date and time management
from django.db import models  # For defining Django models
from django.contrib.auth.models import PermissionsMixin

class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email you provided is invalid!")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_user(self, email=None, password=None, **extra_fields):
        # Ensure regular users have no special permissions
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email=None, password=None, **extra_fields):
        # Superusers will have elevated permissions
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)

    def create_peso_staff(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('user_type', 'PESO')
        return self.create_user(email, password, **extra_fields)

    def create_employer(self, email=None, password=None, company_name='', **extra_fields):
        extra_fields.setdefault('user_type', 'EMPLOYER')
        extra_fields['company_name'] = company_name
        return self.create_user(email, password, **extra_fields)

    def create_job_seeker(self, email=None, password=None, first_name='', middle_name='', last_name='', **extra_fields):
        extra_fields.setdefault('user_type', 'JOB_SEEKER')
        extra_fields['first_name'] = first_name
        extra_fields['middle_name'] = middle_name
        extra_fields['last_name'] = last_name

        return self.create_user(email, password, **extra_fields)
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
        USER_TYPES = (
        ('PESO', 'PESO Staff'),
        ('EMPLOYER', 'Employer'),
        ('JOB_SEEKER', 'Job Seeker'),
    )
    
        email = models.EmailField(blank=True, default='', unique=True)

        # Fields for Staff
        name = models.CharField(max_length=255, blank=True, null=True)
        staff_code = models.CharField(max_length=255, blank=True, null=True)

        # Fields for Job Seeker
        first_name = models.CharField(max_length=255, blank=True, null=True)
        middle_name = models.CharField(max_length=255, blank=True, null=True)
        last_name = models.CharField(max_length=255, blank=True, null=True)

        # Fields for Employer
        company_name = models.CharField(max_length=255, blank=True, null=True)



        user_type = models.CharField(max_length=10, choices=USER_TYPES)
        
        is_active = models.BooleanField(default=True)
        is_superuser = models.BooleanField(default=False)
        is_staff = models.BooleanField(default=True)
        
        date_joined = models.DateTimeField(default=timezone.now)
        last_login = models.DateTimeField(blank=True, null=True)
        
        objects = CustomUserManager()
        
        USERNAME_FIELD = 'email'
        REQUIRED_FIELDS = []  # No additional required fields
        
        def get_full_name(self):
            if self.user_type == 'JOB_SEEKER':
                return f"{self.first_name} {self.last_name}".strip()
            elif self.user_type == 'EMPLOYER':
                return self.company_name
            return "Invalid User"

        
        def get_short_name(self):
            if self.user_type == 'JOB_SEEKER':
                return f"{self.first_name} {self.last_name}".strip()
            elif self.user_type == 'EMPLOYER':
                return self.company_name
            return self.email.split('@')[0]

        def __str__(self):
            return self.email