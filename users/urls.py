from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from users.views import CreateUserView, UserManagerView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("me/", UserManagerView.as_view(), name="manage"),

    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify/", TokenVerifyView.as_view(), name="token_verify"),
]

app_name = "user"
