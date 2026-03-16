from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.serializers import PaymentCreateSerializer, PaymentSerializer
from materials.stripe_service import (
    create_stripe_checkout_session,
    create_stripe_price,
    create_stripe_product,
    retrieve_stripe_session,
)
from users.models import Payment


class CreatePaymentView(APIView):
    """
    Создание платежа через Stripe.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Валидация входных данных через сериализатор
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        course = validated_data.get('course')
        lesson = validated_data.get('lesson')
        
        # Определяем название продукта и сумму
        if course:
            product_name = f"Курс {course.title}"
            amount = int(course.price * 100)  # В копейках
        else:
            product_name = f"Урок {lesson.title}"
            amount = int(lesson.price * 100)  # В копейках
        
        try:
            with transaction.atomic():
                # Создаем продукт в Stripe
                stripe_product = create_stripe_product(product_name)
                
                # Создаем цену в Stripe
                stripe_price = create_stripe_price(
                    product_id=stripe_product.id, 
                    amount=amount
                )
                
                # Создаем сессию для оплаты
                stripe_session = create_stripe_checkout_session(
                    price_id=stripe_price.id,
                    success_url="http://localhost:8000/success/",
                    cancel_url="http://localhost:8000/cancel/",
                )
                
                # Создаем платеж в нашей системе только после успешных запросов в Stripe
                payment = Payment.objects.create(
                    user=request.user,
                    paid_course=course,
                    paid_lesson=lesson,
                    amount=amount / 100,  # Возвращаем в рублях
                    payment_method="stripe",
                    stripe_session_id=stripe_session.id,
                    stripe_payment_url=stripe_session.url,
                )
                
                return Response({
                    "payment_id": payment.id,
                    "payment_url": stripe_session.url,
                    "amount": payment.amount,
                })
                
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentStatusView(APIView):
    """
    Проверка статуса платежа.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, payment_id):
        user_payments = Payment.objects.filter(user=request.user)
        payment = get_object_or_404(user_payments, id=payment_id)
        
        if not payment.stripe_session_id:
            return Response(
                {"error": "Платеж не связан с Stripe"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Получаем статус сессии из Stripe
        stripe_session = retrieve_stripe_session(payment.stripe_session_id)
        
        # Обновляем статус платежа в нашей системе
        payment.is_paid = stripe_session.payment_status == "paid"
        payment.save()
        
        return Response(
            PaymentSerializer(payment, context={'request': request}).data
        )
