from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from notifications.application.dtos.notification_templates.notification_template_create_dto import (
    NotificationTemplateCreateDTO,
)
from notifications.exceptions.exceptions import NotificationDomainError
from notifications.providers.notification_provider import NotificationProvider
from notifications.serializers.notification_templates.notification_template_create_serializer import (
    NotificationTemplateCreateSerializer,
)
from notifications.serializers.notification_templates.notification_template_response_serializer import (
    NotificationTemplateResponseSerializer,
)
from notifications.views.forms.notification_template_form import (
    NotificationTemplateForm,
)


class NotificationTemplateCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = NotificationTemplateForm()
        return render(
            request, "pages/notification_templates/create.html", {"form": form}
        )

    def post(self, request):
        form = NotificationTemplateForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                dto = NotificationTemplateCreateDTO(
                    tenant_id=data["tenant"].id,
                    code=data["code"],
                    name=data["name"],
                    channel=data["channel"],
                    body=data["body"],
                    subject=data.get("subject"),
                    variables=data.get("variables") or [],
                    is_active=data.get("is_active", True),
                )
                NotificationProvider.create_template().execute(dto)
                messages.success(request, "Mẫu thông báo tạo thành công.")
                return redirect("notification_template_list")
            except Exception as e:
                form.add_error(None, str(e))
        return render(
            request, "pages/notification_templates/create.html", {"form": form}
        )


class NotificationTemplateCreateApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NotificationTemplateCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)

        validated_data = serializer.validated_data
        dto = NotificationTemplateCreateDTO(
            tenant_id=validated_data["tenant_id"],
            code=validated_data["code"],
            name=validated_data["name"],
            channel=validated_data["channel"],
            body=validated_data["body"],
            subject=validated_data.get("subject"),
            variables=validated_data.get("variables") or [],
            is_active=validated_data.get("is_active", True),
        )

        try:
            response_dto = NotificationProvider.create_template().execute(dto)
            response_serializer = NotificationTemplateResponseSerializer(response_dto)
            return JsonResponse(response_serializer.data, status=201)
        except NotificationDomainError as e:
            return JsonResponse({"error": str(e)}, status=400)
