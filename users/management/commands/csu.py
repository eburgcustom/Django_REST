from django.core.management.base import BaseCommand
from users.models import User
from decouple import config


class Command(BaseCommand):
    help = "Создание суперпользователя"

    def handle(self, *args, **options):
        email = config('EMAIL_HOST_USER')
        password = config('PASSWORD_FOR_SUPER_USER')
        user = User.objects.create(email=email)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
