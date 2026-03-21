import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name):
    """
    Создает продукт в Stripe.

    Args:
        name (str): Название продукта

    Returns:
        dict: Данные созданного продукта
    """
    product = stripe.Product.create(
        name=name,
        type="service",
    )
    return product


def create_stripe_price(product_id, amount, currency="usd"):
    """
    Создает цену в Stripe.

    Args:
        product_id (str): ID продукта в Stripe
        amount (int): Сумма в копейках
        currency (str): Валюта (по умолчанию usd)

    Returns:
        dict: Данные созданной цены
    """
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount,
        currency=currency,
    )
    return price


def create_stripe_checkout_session(price_id, success_url, cancel_url):
    """
    Создает сессию для оплаты в Stripe.

    Args:
        price_id (str): ID цены в Stripe
        success_url (str): URL для перенаправления после успешной оплаты
        cancel_url (str): URL для перенаправления после отмены оплаты

    Returns:
        dict: Данные созданной сессии
    """
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session


def retrieve_stripe_session(session_id):
    """
    Получает информацию о сессии в Stripe.

    Args:
        session_id (str): ID сессии в Stripe

    Returns:
        dict: Данные сессии
    """
    session = stripe.checkout.Session.retrieve(session_id)
    return session
