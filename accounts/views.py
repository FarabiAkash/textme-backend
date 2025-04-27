from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import UserProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer, 
    UserProfileSerializer, PasswordChangeSerializer
)

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.profile


class UserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            # Check old password
            if not request.user.check_password(serializer.data.get('old_password')):
                return Response({'old_password': ['Wrong password.']}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            request.user.set_password(serializer.data.get('new_password'))
            request.user.save()
            return Response(
                {'detail': 'Password updated successfully'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return all users except those with private profiles (unless it's the current user)"""
        # Exclude users with private profiles (except current user)
        return User.objects.exclude(
            profile__is_profile_private=True
        ).exclude(id=self.request.user.id)