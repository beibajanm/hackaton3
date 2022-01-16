from django.core.mail import send_mail


def send_activation_code(email,activation_code):
    activation_url = f'http://localhost:8000/v1/api/account/activate/{activation_code}'
    message = f'Пожалуйста перейдите по ссылке для активации аккаунта: {activation_url}'

    send_mail('Активация',
              message,
              'test@test.com',
              [email,],
              fail_silently=False
    )