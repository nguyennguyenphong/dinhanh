from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from notifications.application.dtos.notification_templates.notification_template_update_dto import (
    NotificationTemplateUpdateDTO,
)
from notifications.exceptions.exceptions import (
    NotificationDomainError,
    NotificationTemplateNotFoundError,
)
from notifications.models.notification_templates import NotificationTemplate
from notifications.providers.notification_provider import NotificationProvider
from notifications.serializers.notification_templates.notification_template_response_serializer import (
    NotificationTemplateResponseSerializer,
)
from notifications.serializers.notification_templates.notification_template_update_serializer import (
    NotificationTemplateUpdateSerializer,
)
from notifications.views.forms.notification_template_base_form import (
    NotificationTemplateBaseForm,
)


class NotificationTemplateUpdateView(LoginRequiredMixin, View):

    def get(self, request, pk):
        template = get_object_or_404(NotificationTemplate, pk=pk)
        form = NotificationTemplateBaseForm(instance=template)
        return render(
            request,
            "pages/notification_templates/update.html",
            {"form": form, "object": template},
        )

    def post(self, request, pk):
        template = get_object_or_404(NotificationTemplate, pk=pk)
        form = NotificationTemplateBaseForm(request.POST, instance=template)
        if form.is_valid():
            try:
                data = form.cleaned_data
                dto = NotificationTemplateUpdateDTO(
                    id=pk,
                    tenant_id=data["tenant"].id,
                    code=data["code"],
                    name=data["name"],
                    channel=data["channel"],
                    body=data["body"],
                    subject=data.get("subject"),
                    variables=data.get("variables") or [],
                    is_active=data.get("is_active", True),
                )
                NotificationProvider.update_template().execute(dto)
                messages.success(request, "Mẫu thông báo cập nhật thành công.")
                return redirect("notification_template_list")
            except Exception as e:
                form.add_error(None, str(e))
        return render(
            request,
            "pages/notification_templates/update.html",
            {"form": form, "object": template},
        )


class NotificationTemplateUpdateApiView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        serializer = NotificationTemplateUpdateSerializer(
            data=request.data, context={"template_id": pk}
        )
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)

        validated_data = serializer.validated_data
        dto = NotificationTemplateUpdateDTO(
            id=pk,
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
            response_dto = NotificationProvider.update_template().execute(dto)
            response_serializer = NotificationTemplateResponseSerializer(response_dto)
            return JsonResponse(response_serializer.data)
        except NotificationTemplateNotFoundError as e:
            return JsonResponse({"error": str(e)}, status=404)
        except NotificationDomainError as e:
            return JsonResponse({"error": str(e)}, status=400)
