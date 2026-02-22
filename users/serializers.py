from rest_framework import serializers

from materials.serializers import CourseSerializer, LessonSerializer

from .models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.
    Преобразует данные платежа в JSON и обратно.
    """

    user_email = serializers.EmailField(source="user.email", read_only=True)
    paid_course = CourseSerializer(read_only=True)
    paid_lesson = LessonSerializer(read_only=True)
    payment_method_display = serializers.CharField(
        source="get_payment_method_display", read_only=True
    )

    class Meta:
        model = Payment
        fields = "__all__"
