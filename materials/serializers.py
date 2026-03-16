from rest_framework import serializers

from .models import Course, Lesson, Subscription
from .validators import validate_youtube_url
from users.models import Payment


class PaymentCreateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False)
    lesson_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        course_id = attrs.get('course_id')
        lesson_id = attrs.get('lesson_id')
        
        if not course_id and not lesson_id:
            raise serializers.ValidationError(
                "Необходимо указать course_id или lesson_id"
            )
        
        if course_id and lesson_id:
            raise serializers.ValidationError(
                "Нельзя указывать одновременно course_id и lesson_id"
            )
        
        # Проверяем существование курса
        if course_id:
            try:
                attrs['course'] = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                raise serializers.ValidationError(
                    f"Курс с id={course_id} не найден"
                )
        
        # Проверяем существование урока
        if lesson_id:
            try:
                attrs['lesson'] = Lesson.objects.get(id=lesson_id)
            except Lesson.DoesNotExist:
                raise serializers.ValidationError(
                    f"Урок с id={lesson_id} не найден"
                )
        
        return attrs


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson.
    Преобразует данные урока в JSON и обратно.
    """

    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    video_url = serializers.URLField(validators=[validate_youtube_url])

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
            "price",
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
    is_subscribed = serializers.SerializerMethodField()

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
            "is_subscribed",
            "price",
        ]
        read_only_fields = ["id", "owner"]

    def get_lessons_count(self, obj):
        """Возвращает количество уроков в курсе."""
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.
    Преобразует данные платежа в JSON и обратно.
    """
    
    user_email = serializers.EmailField(source="user.email", read_only=True)
    course_title = serializers.CharField(source="paid_course.title", read_only=True)
    lesson_title = serializers.CharField(source="paid_lesson.title", read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "user_email",
            "paid_course",
            "course_title",
            "paid_lesson",
            "lesson_title",
            "amount",
            "payment_method",
            "payment_date",
            "stripe_session_id",
            "stripe_payment_url",
            "is_paid",
        ]
        read_only_fields = ["id", "user", "payment_date", "stripe_session_id", "stripe_payment_url"]
