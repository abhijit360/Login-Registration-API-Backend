import hashlib
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser,AbstractBaseUser, BaseUserManager, PermissionsMixin, UserManager
from django.contrib.auth.hashers import make_password
import datetime
from datetime import timezone

# Create your models here.

# Bank details
class BankAccount(models.Model):
    choices = [
        ("BOI", "Bank of India"),
        ("SBI", "State Bank of India"),
        ("ICI","ICICI Bank"),
        ("HDF", "HDFC Bank"),
        ("IIB","IndusInd Bank")
    ]
    name = models.CharField(max_length=3, choices=choices, null=True, blank=True)
    account_num = models.IntegerField(null=True, blank=True)
    IFSC_Code = models.IntegerField(null=True, blank=True)

    def __str__(self):
        try:
            return f"{self.user.name}'s Bank Account"
        except:
            return f"{self.account_num}"




class CustomUser(models.Model):
    id = models.UUIDField(editable=False, unique=True, primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.IntegerField(unique=True)
    password = models.CharField(max_length=100)
    bank_account = models.OneToOneField(BankAccount, on_delete=models.CASCADE , unique=True , null=True , blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["phone","name"]

    def save(self, *args, **kwargs):
        self.password = hashlib.md5(self.password.encode()).digest()
        super(CustomUser, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name 
    
class JWT_storedVal(models.Model):
    jwt_token = models.CharField(max_length=250, unique=True)
    user_id = models.CharField(max_length=50, unique=True)
    

# class myUserManager(BaseUserManager):
#     def create_user(self,email,phone, password=None, **extra_fields):
#         if not email:
#             raise ValueError("The Email field is required")
#         if not phone:
#             raise ValueError("The Phone field must be set")
    
#         email = self.normalize_email(email)
#         user = self.model(email=email, phone=phone, **extra_fields)
#         user.set_password(password)
#         user.save(using=self.db)
#         return user
    
#     def create_superuser(self, email, phone, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
        
#         if not extra_fields.get('is_staff'):
#             raise ValueError('Superuser must have is_staff=True.')
#         if not extra_fields.get('is_superuser'):
#             raise ValueError('Superuser must have is_superuser=True.')
        
#         return self.create_user(email, phone, password, **extra_fields)


# class myUser(AbstractBaseUser,PermissionsMixin):
#     email = models.EmailField(unique=True)
#     phone = models.IntegerField(unique=True)
#     bank_account = models.OneToOneField(BankAccount, on_delete=models.CASCADE, unique=True, null=True, blank=True)
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=30)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

    
#     # deal with creation and save logic in a custom save
#     date_joined = models.DateTimeField(editable=False)
#     modified = models.DateTimeField()  

#     objects = myUserManager()

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = ['phone']
#     # required fields are required when creating a user via the amnagement command createsuperuser
#     # It is not requried for create_user

#     def save(self, *args, **kwargs):
#         ''' On save, update timestamps '''
#         if not self.id:
#             # checks if the user is being created for the first time
#             self.date_joined = datetime.datetime.now()
#         self.modified = datetime.datetime.now()
#         return super(myUser, self).save(*args, **kwargs)
  
#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"
    
    
