from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from materials.models import Course, Lesson
from users.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = "Создает тестовые платежи"

    def handle(self, *args, **options):
        # Получаем или создаем тестового пользователя
        user, created = User.objects.get_or_create(
            email="test@example.com",
            defaults={"first_name": "Test", "last_name": "User"},
        )

        # Получаем первый курс и урок (если существуют)
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        if course:
            Payment.objects.get_or_create(
                user=user,
                paid_course=course,
                defaults={"amount": 5000.00, "payment_method": "transfer"},
            )
            self.stdout.write(
                self.style.SUCCESS(f"Создан платеж за курс: {course.title}")
            )

        if lesson:
            Payment.objects.get_or_create(
                user=user,
                paid_lesson=lesson,
                defaults={"amount": 500.00, "payment_method": "cash"},
            )
            self.stdout.write(
                self.style.SUCCESS(f"Создан платеж за урок: {lesson.title}")
            )

        self.stdout.write(self.style.SUCCESS("Платежи успешно созданы"))
