from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class IsSupplier(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SUPPLIER'

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'CUSTOMER'

class IsDeliveryPerson(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'DELIVERY'

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        return obj.customer == request.user

class IsAdminOrSupplier(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.role == 'ADMIN' or request.user.role == 'SUPPLIER'))