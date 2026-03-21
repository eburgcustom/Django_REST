from django.conf import settings
from django.db import models


class Course(models.Model):
    """
    Модель курса.
    Содержит основную информацию о курсе.
    """

    title = models.CharField(max_length=200, verbose_name="Название")
    preview = models.ImageField(
        upload_to="courses/", blank=True, null=True, verbose_name="Превью"
    )
    description = models.TextField(verbose_name="Описание")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Цена курса"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    """
    Модель урока.
    Связана с курсом через ForeignKey.
    """

    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    preview = models.ImageField(
        upload_to="lessons/", blank=True, null=True, verbose_name="Превью"
    )
    video_url = models.URLField(verbose_name="Ссылка на видео")
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Владелец",
        null=True,
        blank=True,
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Цена урока"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class Subscription(models.Model):
    """
    Модель подписки пользователя на курс.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = [
            "user",
            "course",
        ]  # Уникальная подписка для пользователя и курса

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"
