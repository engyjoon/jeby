from django.core.mail import send_mail

send_mail(
    'Hello',
    'Email test',
    'jebyhouse@gmail.com',
    ['engyjoon@gmail.com'],
    fail_silently=False,
)
