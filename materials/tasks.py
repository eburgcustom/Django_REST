from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings


@shared_task
def check_inactive_users():
    """
    Проверяет пользователей, которые не заходили более месяца, и блокирует их.
    """
    try:
        # Дата месяц назад
        month_ago = timezone.now() - timedelta(days=30)
        
        # Импортируем User здесь чтобы избежать circular import
        from users.models import User
        
        # Находим пользователей, которые не заходили более месяца
        inactive_users = User.objects.filter(
            last_login__lt=month_ago,
            is_active=True
        )
        
        blocked_count = 0
        
        for user in inactive_users:
            # Блокируем пользователя
            user.is_active = False
            user.save(update_fields=['is_active'])
            blocked_count += 1
            
            # Отправляем уведомление на email
            try:
                send_mail(
                    subject='Ваш аккаунт был заблокирован',
                    message=f'Здравствуйте, {user.username}!\n\n'
                           f'Ваш аккаунт был заблокирован, так как вы не заходили в систему более 30 дней.\n\n'
                           f'Для разблокировки обратитесь к администратору.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                # Игнорируем ошибки отправки email
                pass
        
        return f"Заблокировано {blocked_count} неактивных пользователей"
        
    except Exception as e:
        return f"Ошибка при проверке неактивных пользователей: {str(e)}"


@shared_task
def send_course_update_email(course_id):
    """
    Асинхронная отправка писем подписчикам об обновлении курса.
    """
    from .models import Course, Subscription

    try:
        course = Course.objects.get(id=course_id)

        # Получаем всех подписчиков курса
        subscriptions = Subscription.objects.filter(course=course)

        if not subscriptions.exists():
            return f"No subscribers for course {course_id}"

        # Формируем список email подписчиков
        recipient_emails = [sub.user.email for sub in subscriptions]

        # Отправляем письмо
        send_mail(
            subject=f'Обновление курса: {course.title}',
            message=f'Здравствуйте! Курс "{course.title}" был обновлен.\n\n'
                   f'Описание: {course.description[:200]}...\n\n'
                   f'Посмотреть обновления можно в вашем личном кабинете.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_emails,
            fail_silently=False,
        )

        return f"Email sent to {len(recipient_emails)} subscribers for course {course_id}"

    except Course.DoesNotExist:
        return f"Course {course_id} not found"
    except Exception as e:
        return f"Error sending email: {str(e)}"


@shared_task
def send_course_update_email_with_delay(course_id):
    """
    Асинхронная отправка писем с проверкой 4 часов.
    """
    from .models import Course

    try:
        course = Course.objects.get(id=course_id)

        # Проверяем, не обновлялся ли курс за последние 4 часа
        four_hours_ago = timezone.now() - timedelta(hours=4)

        if course.updated_at and course.updated_at > four_hours_ago:
            return f"Курс {course_id} был обновлен менее 4 часов назад, электронная почта была пропущена"

        # Отправляем письмо
        result = send_course_update_email.delay(course_id)
        
        return f"Уведомление для курса {course_id} отправлено"

    except Course.DoesNotExist:
        return f"Курс {course_id} не найден"
