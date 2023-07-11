from rest_framework import serializers
from .models import CustomUser, BankAccount, JWT_storedVal

class JWT_storedValSerializer(serializers.ModelSerializer):
    model = JWT_storedVal
    fields="__all__"


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ['password','bank_account',]

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ['password','bank_account']

class UserBankDetailsSerializer(serializers.ModelSerializer):
    bank_account = BankAccountSerializer()

    class Meta:
        model = CustomUser
        exclude = ['password']

class UserUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_email = serializers.EmailField(required=False)
    phone =  serializers.IntegerField()
    password = serializers.CharField(max_length=100)

class myUserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone =  serializers.IntegerField()
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=100)


# class myUserSerializer(serializers.Serializer):
#     class Meta:
#         model = myUser
#         fields= ['email','last_name','first_name','phone']
