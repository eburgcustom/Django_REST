from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsOwnerOrModerator

from .models import Course, Lesson, Subscription
from .paginators import StandardPagination
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Course.
    Обеспечивает полный CRUD для курсов.
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        # Обычные пользователи видят только свои курсы
        user = self.request.user
        if user.groups.filter(name="moderator").exists():
            return Course.objects.all().order_by("id")
        return Course.objects.filter(owner=user).order_by("id")

    def get_permissions(self):
        if self.action == "create":
            # Создание курсов - только авторизованные пользователи
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ["update", "partial_update"]:
            # Редактирование - владелец или модератор
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        elif self.action == "destroy":
            # Удаление - владелец или модератор
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        else:
            # Просмотр - авторизованные (с фильтрацией по владельцу в get_queryset)
            self.permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        # Автоматически привязываем курс к текущему пользователю
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    """
    APIView для получения списка уроков и создания нового урока.
    GET - возвращает все уроки (с фильтрацией по владельцу)
    POST - создает новый урок
    """

    serializer_class = LessonSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        # Обычные пользователи видят только свои уроки
        user = self.request.user
        if user.groups.filter(name="moderator").exists():
            return Lesson.objects.all().order_by("id")
        return Lesson.objects.filter(owner=user).order_by("id")

    def get_permissions(self):
        if self.request.method == "POST":
            # Создание уроков - только обычные пользователи (не модераторы)
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            # Просмотр уроков - авторизованные (с фильтрацией по владельцу в get_queryset)
            self.permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        # Проверяем, что пользователь не модератор
        if self.request.user.groups.filter(name="moderator").exists():
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Модераторы не могут создавать уроки")
        # Автоматически привязываем урок к текущему пользователю
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    APIView для работы с конкретным уроком.
    GET - получение урока по id
    PUT/PATCH - обновление урока
    DELETE - удаление урока
    """

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()

    def get_queryset(self):
        # Обычные пользователи видят только свои уроки
        user = self.request.user
        if user.groups.filter(name="moderator").exists():
            return Lesson.objects.all().order_by("id")
        return Lesson.objects.filter(owner=user).order_by("id")

    def get_permissions(self):
        if self.request.method == "GET":
            # Просмотр - авторизованные (с фильтрацией по владельцу в get_queryset)
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.request.method in ["PUT", "PATCH"]:
            # Редактирование - владелец или модератор
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        elif self.request.method == "DELETE":
            # Удаление - авторизованные (с фильтрацией по владельцу в get_queryset)
            self.permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in self.permission_classes]


class SubscriptionAPIView(APIView):
    """
    APIView для управления подписками на курсы.
    POST - подписка/отписка от курса
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "Не указан ID курса"}, status=status.HTTP_400_BAD_REQUEST
            )

        course_item = get_object_or_404(Course, id=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        # Если подписка у пользователя на этот курс есть - удаляем ее
        if subs_item.exists():
            subs_item.delete()
            message = "подписка удалена"
        # Если подписки у пользователя на этот курс нет - создаем ее
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"

        # Возвращаем ответ в API
        return Response({"message": message})
