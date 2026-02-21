from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics

from .models import Payment
from .serializers import PaymentSerializer


class PaymentListView(generics.ListAPIView):
    """
    APIView для получения списка платежей с фильтрацией и сортировкой.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        "paid_course": ["exact"],
        "paid_lesson": ["exact"],
        "payment_method": ["exact"],
    }
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]  # сортировка по умолчанию - новые платежи первые
