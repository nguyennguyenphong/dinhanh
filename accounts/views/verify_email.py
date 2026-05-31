from django.shortcuts import render

def verify_email(request):
    return render(request, 'pages/verify_email.html')