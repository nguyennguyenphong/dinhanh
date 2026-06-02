from django.shortcuts import render

def list_tenant(request):
    return render(request, "pages/list.html")