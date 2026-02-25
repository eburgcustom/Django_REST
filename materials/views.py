from rest_framework import viewsets, generics, permissions
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Course.
    Обеспечивает полный CRUD для курсов.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]


class LessonListCreateView(generics.ListCreateAPIView):
    """
    APIView для получения списка уроков и создания нового урока.
    GET - возвращает все уроки
    POST - создает новый урок
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    APIView для работы с конкретным уроком.
    GET - получение урока по id
    PUT/PATCH - обновление урока
    DELETE - удаление урока
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
