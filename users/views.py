from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserRegisterSerializer, UserRetrieveSerializer, UserSerializer
from .permissions import IsOwner



class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        user = User.objects.get(phone=request.data["phone"])
        user.last_login = timezone.now()
        user.save()
        return super().post(request, args, kwargs)


class UserRegisterAPIView(generics.CreateAPIView):
    """
    Register new user. For any user
    """

    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().post(request, *args, **kwargs)


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """
    Get user by id. With fields "email", "first_name", "phone", "country", "avatar" for any authenticated user
    and extra "last_name", "payment_history" for owner user
    """

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.user == self.get_object():
            return UserRetrieveSerializer
        else:
            return UserSerializer


class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserRetrieveSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]

    def put(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().put(request, *args, **kwargs)


class UserDestroyAPIView(generics.DestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]

    def destroy(self, request: Request, *args: tuple, **kwargs: dict) -> Response:
        return super().destroy(request, *args, **kwargs)


class UserEmailVerificationAPIView(APIView):
    """
    Class for verification of user email

    return: Response of status of verification
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, token: str) -> Response:
        try:
            user = User.objects.get(token=token)
            user.is_active = True
            user.save()

            return Response({"status": "success", "message": "Верификация по email прошла успешно"})
        except Exception as e:
            return Response({"status": "fail", "message": str(e)})
