from django.shortcuts import render

def password_reset_complete(request):
    return render(request, 'pages/password_reset_complete.html')