# Url account's module
from django.urls import path

from accounts.views.auth.login import login
from accounts.views.auth.password_reset import password_reset
from accounts.views.auth.password_reset_complete import password_reset_complete
from accounts.views.auth.password_reset_confirm import password_reset_confirm
from accounts.views.auth.register import register
from accounts.views.auth.verify_email import verify_email

urlpatterns = [
    path("login/", login, name="login"),
    path("register/", register, name="register"),
    path("password_reset/", password_reset, name="password_reset"),
    path(
        "password_reset_confirm/", password_reset_confirm, name="password_reset_confirm"
    ),
    path("verify_email/", verify_email, name="verify_email"),
    path(
        "password_reset_complete/",
        password_reset_complete,
        name="password_reset_complete",
    ),
]
