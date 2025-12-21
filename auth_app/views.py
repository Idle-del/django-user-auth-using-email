from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets

from .serializers import UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

from rest_framework import serializers

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'register':
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'status': 'User created', 'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            # Look up the user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        # Authenticate using username since Django's auth requires it
        self.user = authenticate(username=user.username, password=password)

        if not self.user:
            raise serializers.ValidationError("Invalid email or password")

        data = super().validate({
            "username": user.username,
            "password": password
        })
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['id'] = self.user.id
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["email"] = user.email
        return token

    # Modify fields so we receive 'email' instead of 'username'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField()
        self.fields.pop('username')

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainSerializer
    permission_classes = [AllowAny]