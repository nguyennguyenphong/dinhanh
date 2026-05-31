# Path: accounts/views/login.py

from django.shortcuts import render

def login(request):
    return render(request, 'pages/login.html')