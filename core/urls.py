"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from dashboard.views import dashboard
from media.views.views import ckeditor5_dummy_upload

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    # dashboard
    path("", dashboard, name="dashboard"),
    # accounts app
    path("", include("accounts.urls")),
    # tenants
    path("tenants/", include("tenants.urls")),
    # menus
    path("menus/", include("menus.urls")),
    # notifications
    path("notifications/", include("notifications.urls")),
    # assets
    path("", include("assets.urls")),
    # branches
    path("", include("branches.urls")),
    # ckeditor5
    path(
        "media/ck5-dummy-upload/",
        ckeditor5_dummy_upload,
        name="ck_editor_5_upload_file",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.page_not_found"
handler500 = "core.views.page_server_error_500"
