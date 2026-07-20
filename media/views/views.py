from django.http import HttpResponseForbidden


def ckeditor5_dummy_upload(request):
    return HttpResponseForbidden("Tính năng upload ảnh bị tắt.")
