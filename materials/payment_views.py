from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.stripe_service import (create_stripe_checkout_session,
                                      create_stripe_price,
                                      create_stripe_product,
                                      retrieve_stripe_session)
from users.models import Payment


class CreatePaymentView(APIView):
    """
    Создание платежа через Stripe.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Получаем данные из запроса
        course_id = request.data.get("course_id")
        lesson_id = request.data.get("lesson_id")

        if not course_id and not lesson_id:
            return Response(
                {"error": "Необходимо указать course_id или lesson_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Создаем платеж в нашей системе
        payment = Payment.objects.create(
            user=request.user,
            paid_course_id=course_id,
            paid_lesson_id=lesson_id,
            amount=0,  # Будет установлено после создания цены
            payment_method="stripe",
        )

        # Определяем название продукта и сумму
        if course_id:
            product_name = f"Курс {payment.paid_course.title}"
            amount = int(payment.paid_course.price * 100)  # В копейках
        else:
            product_name = f"Урок {payment.paid_lesson.title}"
            amount = int(payment.paid_lesson.price * 100)  # В копейках

        try:
            # Создаем продукт в Stripe
            stripe_product = create_stripe_product(product_name)

            # Создаем цену в Stripe
            stripe_price = create_stripe_price(
                product_id=stripe_product.id, amount=amount
            )

            # Создаем сессию для оплаты
            stripe_session = create_stripe_checkout_session(
                price_id=stripe_price.id,
                success_url="http://localhost:8000/success/",
                cancel_url="http://localhost:8000/cancel/",
            )

            # Обновляем платеж в нашей системе
            payment.stripe_session_id = stripe_session.id
            payment.stripe_payment_url = stripe_session.url
            payment.amount = amount / 100  # Возвращаем в рублях
            payment.save()

            # Возвращаем ссылку на оплату
            return Response(
                {
                    "payment_id": payment.id,
                    "payment_url": stripe_session.url,
                    "amount": payment.amount,
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentStatusView(APIView):
    """
    Проверка статуса платежа.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)

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
                {
                    "payment_id": payment.id,
                    "status": stripe_session.payment_status,
                    "is_paid": payment.is_paid,
                    "amount": payment.amount,
                }
            )

        except Payment.DoesNotExist:
            return Response(
                {"error": "Платеж не найден"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
