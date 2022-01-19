from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.serializers import RegisterSerializer, LoginSerializer,ForgotPasswordSerializer,ForgotPasswordCompleteSerializer


class RegisterView(APIView):
    def post(self,request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Вы успешно зарегистрировались,На вашу электронную почту выслано сообщение!',status=status.HTTP_201_CREATED)


class ActivateView(APIView):
    def get(self,request,activation_code):
        User = get_user_model()
        user = get_object_or_404(User,activation_code=activation_code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response('Вы успешно активировали ваш аккаунт!',status=status.HTTP_200_OK)


class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self,request):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response('Вы успешно разлогинились',status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    def post(self, request):
        data = request.data
        serializer = ForgotPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.send_reset_email()
        return Response('Вам выслан код подтверждения')


class ForgotPasswordCompleteView(APIView):
    def post(self, request):
        data = request.data
        serializer = ForgotPasswordCompleteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.set_new_pass()
        return Response('Вы успешно восстановили пароль!')