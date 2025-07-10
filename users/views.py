from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import *
from .serializers import *
from .permissions import *
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
    
        if self.action in ['create', 'update']:
            permission_classes.append(IsAdmin)
        
        return [permission() for permission in permission_classes]
    def update(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            if request.user.id != int(kwargs.get('pk')):
                return Response({'detail': 'You do not have permission to update this user.'}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            if request.user.id != int(kwargs.get('pk')):
                return Response({'detail': 'You do not have permission to update this user.'}, status=403)
        return super().partial_update(request, *args, **kwargs)
    def list(self, request, *args, **kwargs):
        user = request.user
        print(f"DEBUG: Logged-in user = {user.username}, Role = {user.role}")
        if user.role == 'ADMIN':
            return super().list(request, *args, **kwargs)
        # Return only own user data wrapped in list
        serializer = self.get_serializer(user)
        return Response([serializer.data])
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated]) ##createing end for custome user !
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class RegisterViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "User created successfully",
        }, status=status.HTTP_201_CREATED)
class LoginView(GenericAPIView, CreateModelMixin):
    serializer_class = LoginSerializer
    permission_classes = []  # Allow unauthenticated access

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate or get token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            "token": token.key,
            "user_id": user.id,
            "username": user.username,
            "role" : user.role
        })