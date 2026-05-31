# Url account's module
from django.urls import path
from accounts.views.login import login
from accounts.views.register import register
from accounts.views.password_reset import password_reset
from accounts.views.password_reset_confirm import password_reset_confirm
from accounts.views.verify_email import verify_email

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('password_reset/', password_reset, name='password_reset'),
    path('password_reset_confirm/', password_reset_confirm, name='password_reset_confirm'),
    path('verify_email/', verify_email, name='verify_email'),
]