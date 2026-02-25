from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from users.apps import UsersConfig

from .views import (CustomTokenObtainPairView, PaymentListView, UserDetailView,
                    UserListView, UserRegistrationView)

app_name = UsersConfig.name

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("payments/", PaymentListView.as_view(), name="payment-list"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
