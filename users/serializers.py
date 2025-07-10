from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from .models import *
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'address']
        read_only_fields = ['role']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','role','phone']

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password', 'password2', 'email', 'role', 'phone', 'address']
        extra_kwargs = {
            'phone': {'required': False},
            'address': {'required': False},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        if attrs.get('role') in ['ADMIN', 'DELIVERY']:
            raise serializers.ValidationError({"role": "You cannot register as this role."})# Only allow certain roles to be registered via API 
        
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data['email'],
            role=validated_data.get('role', 'CUSTOMER'),
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        role = attrs.get('role')
        user = authenticate(username=username, password=password, role = role)
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if user.role != role:
            raise serializers.ValidationError(f"User doesn't have the '{role}' role")
        
        attrs['user'] = user
        return attrs