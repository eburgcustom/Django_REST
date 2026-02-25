from rest_framework import viewsets, generics, permissions
from users.permissions import IsModerator, IsModeratorOrReadOnly
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Course.
    Обеспечивает полный CRUD для курсов.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            # Создание курсов запрещено для модераторов
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            # Удаление курсов запрещено для модераторов
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        else:
            # Просмотр и редактирование - модераторы могут
            self.permission_classes = [permissions.IsAuthenticated, IsModeratorOrReadOnly]
        return [permission() for permission in self.permission_classes]


class LessonListCreateView(generics.ListCreateAPIView):
    """
    APIView для получения списка уроков и создания нового урока.
    GET - возвращает все уроки
    POST - создает новый урок (запрещено модераторам)
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            # Создание уроков запрещено для модераторов
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        else:
            # Просмотр уроков - модераторы могут
            self.permission_classes = [permissions.IsAuthenticated, IsModeratorOrReadOnly]
        return [permission() for permission in self.permission_classes]


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    APIView для работы с конкретным уроком.
    GET - получение урока по id
    PUT/PATCH - обновление урока
    DELETE - удаление урока (запрещено модераторам)
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            # Удаление уроков запрещено для модераторов
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        else:
            # Просмотр и редактирование - модераторы могут
            self.permission_classes = [permissions.IsAuthenticated, IsModeratorOrReadOnly]
        return [permission() for permission in self.permission_classes]
