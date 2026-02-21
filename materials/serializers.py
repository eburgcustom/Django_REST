from rest_framework import serializers
from .models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course.
    Преобразует данные курса в JSON и обратно.
    """
    class Meta:
        model = Course
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson.
    Преобразует данные урока в JSON и обратно.
    """
    class Meta:
        model = Lesson
        fields = '__all__'
