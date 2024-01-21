from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from users.views import UserSignUpView

urlpatterns = [
    path("sign-up/", UserSignUpView.as_view(), name="sign-up"),
    path(
        "login/",
        LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
]
