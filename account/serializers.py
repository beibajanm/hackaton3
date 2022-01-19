from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from rest_framework import serializers
from account.tasks import send_activation_code, send_activation_code_email
from account.models import MyUser
from account.utils import send_activation_code

MyUser = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6,write_only=True)
    password_confirm = serializers.CharField(min_length=6,write_only=True)

    class Meta:
        model = MyUser
        fields = ('email','password','password_confirm')

    def validate(self,validated_data):
        password = validated_data.get('password')
        password_confirm = validated_data.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Пароли не совпадают')
        return validated_data

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        user = MyUser.objects.create_user(email=email,password=password)
        send_activation_code_email.delay(email=user.email,activation_code=user.activation_code)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(label='Password',style={'input_type': 'password'},trim_whitespace=False)

    def validate(self,attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),email=email,password=password)
            if not user:
                message = 'Невозможно войти с предоставленными учетными данными'
                raise serializers.ValidationError(message,code='authorization')
        else:
            message = 'Должен включать "email" и "пароль".'
            raise serializers.ValidationError(message,code='authorization')

        attrs['user'] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if not MyUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь с таким email не существует')
        return email

    def send_reset_email(self):
        email = self.validated_data.get('email')
        user = MyUser.objects.get(email=email)
        user.create_activation_coder()
        message = f'код для смены пароля {user.activation_code}'
        send_mail(
            'Смена пароля',
            message,
            'test@gmail.com',
            [email]
        )


class ForgotPasswordCompleteSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
    new_password_confirm = serializers.CharField(required=True, min_length=6)

    class Meta:
        model = MyUser
        fields = ('code','new_password','new_password_confirm',)

    def validate_code(self, code):
        if not MyUser.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError('Неверный код активации')
        return code

    def validate(self, validated_data):
        new_password = validated_data.get('new_password')
        new_password_confirm = validated_data.get('new_password_confirm')
        if new_password != new_password_confirm:
            raise serializers.ValidationError('Неверный пароль или его подтверждение')
        return validated_data

    def set_new_pass(self):
        code = self.validated_data.get('code')
        new_password = self.validated_data.get('new_password')
        user = MyUser.objects.get(activation_code=code)
        user.set_password(new_password)
        user.save()