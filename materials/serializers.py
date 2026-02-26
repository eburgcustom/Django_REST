from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson.
    Преобразует данные урока в JSON и обратно.
    """

    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "description",
            "preview",
            "video_url",
            "course",
            "owner",
            "owner_email",
        ]
        read_only_fields = ["id", "owner"]


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course.
    Преобразует данные курса в JSON и обратно.
    """

    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "preview",
            "description",
            "owner",
            "owner_email",
            "lessons_count",
            "lessons",
        ]
        read_only_fields = ["id", "owner"]

    def get_lessons_count(self, obj):
        """Возвращает количество уроков в курсе."""
        return obj.lessons.count()
