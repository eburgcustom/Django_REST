from rest_framework import generics, permissions, viewsets

from users.permissions import IsOwnerOrModerator

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Course.
    Обеспечивает полный CRUD для курсов.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_queryset(self):
        # Обычные пользователи видят только свои курсы
        user = self.request.user
        if user.groups.filter(name="moderator").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

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

    def get_queryset(self):
        # Обычные пользователи видят только свои уроки
        user = self.request.user
        if user.groups.filter(name="moderator").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        if self.request.method == "POST":
            # Создание уроков - только авторизованные пользователи
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            # Просмотр уроков - авторизованные (с фильтрацией по владельцу в get_queryset)
            self.permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
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

    def get_permissions(self):
        if self.request.method == "GET":
            # Просмотр - владелец или модератор
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        elif self.request.method in ["PUT", "PATCH"]:
            # Редактирование - владелец или модератор
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        elif self.request.method == "DELETE":
            # Удаление - владелец или модератор
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        return [permission() for permission in self.permission_classes]
