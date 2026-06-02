from django.shortcuts import render

def create_tenant(request):
    return render(request, "pages/create.html")