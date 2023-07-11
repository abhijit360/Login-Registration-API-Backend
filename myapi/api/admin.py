from django.contrib import admin
from .models import CustomUser,BankAccount, JWT_storedVal
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(JWT_storedVal)
admin.site.register(BankAccount)
