from django import forms

from notifications.models.notifications import Notification
from notifications.views.forms.notification_template_form import TailwindFormMixin


class NotificationForm(TailwindFormMixin, forms.ModelForm):

    class Meta:
        model = Notification
        fields = [
            "tenant_id",
            "template",
            "recipient_type",
            "recipient_id",
            "recipient_phone",
            "recipient_email",
            "channel",
            "subject",
            "body",
            "status",
            "ref_type",
            "ref_id",
        ]
        widgets = {
            "status": forms.Select(),
        }
