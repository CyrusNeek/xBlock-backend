from rest_framework_simplejwt.tokens import RefreshToken
from ..serializers import MyTokenObtainPairSerializer, RegisterSerializer, OtpTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model

User = get_user_model()


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class OtpTokenObtainPairView(TokenObtainPairView):
    serializer_class = OtpTokenObtainPairSerializer



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(email=request.data["email"])
        refresh = RefreshToken.for_user(user)

        response.data["refresh"] = str(refresh)
        response.data["access"] = str(refresh.access_token)

        return response
