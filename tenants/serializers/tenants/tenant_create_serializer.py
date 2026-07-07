import json
import re

from rest_framework import serializers

from tenants.constants import (
    PLAN_LIMITS,
    PLAN_STANDARD,
)
from tenants.models.tenants import Tenant


class TenantCreateSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=30,
        min_length=5,
        trim_whitespace=True,
        error_messages={"min_length": "Mã tenant phải có ít nhất 5 ký tự."},
    )

    name = serializers.CharField(
        max_length=255,
        min_length=5,
        trim_whitespace=True,
        error_messages={"min_length": "Tên tenant phải có ít nhất 5 ký tự."},
    )

    domain = serializers.CharField(
        max_length=255, required=False, allow_null=True, allow_blank=True
    )

    logo_url = serializers.CharField(
        max_length=500,
        required=False,
        allow_null=True,
        allow_blank=True,
        help_text="URL của logo sau khi upload",
    )

    primary_color = serializers.CharField(max_length=7, default="#3B82F6")

    plan = serializers.ChoiceField(choices=Tenant.PLAN_CHOICES, default="STANDARD")

    currency = serializers.ChoiceField(choices=Tenant.CURRENCY_CHOICES, default="VND")

    exchange_rate = serializers.DecimalField(
        max_digits=12, decimal_places=4, default=1.0000
    )

    default_language = serializers.ChoiceField(
        choices=Tenant.LANGUAGE_CHOICES, default="vi"
    )

    timezone = serializers.ChoiceField(
        choices=Tenant.TIMEZONE_CHOICES, default="Asia/Ho_Chi_Minh"
    )

    is_active = serializers.BooleanField(default=True)

    settings = serializers.JSONField(default=dict, required=False)

    subscription_started_at = serializers.DateTimeField(required=False, allow_null=True)

    subscription_expires_at = serializers.DateTimeField(required=False, allow_null=True)

    max_users = serializers.IntegerField(required=False, allow_null=False, default=10)

    max_branches = serializers.IntegerField(required=False, allow_null=False, default=1)

    max_vehicles = serializers.IntegerField(
        required=False, allow_null=False, default=50
    )

    def validate_code(self, value):
        if Tenant.objects.filter(code=value).exists():
            raise serializers.ValidationError("Mã tenant đã tồn tại.")

        if not value:
            raise serializers.ValidationError("Mã tenant khóa.")

        return value

    def validate_domain(self, value):
        if not value:
            return value

        if not value.startswith("https://"):
            raise serializers.ValidationError("Domain phải bắt đầu bằng https://")

        return value

    def validate_primary_color(self, value):
        if not value:
            return value

        hex_regex = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
        if not re.match(hex_regex, value):
            raise serializers.ValidationError(
                "Mã màu không hợp lệ. Định dạng chuẩn là #Hex (Ví dụ: #3B82F6)."
            )

        return value

    def validate_settings(self, value):
        if not value:
            return {}

        if isinstance(value, str):
            try:
                parsed_value = json.loads(value)

                if not isinstance(parsed_value, dict):
                    raise serializers.ValidationError(
                        "Dữ liệu settings phải là một JSON Object (bắt đầu bằng { và kết thúc bằng })."
                    )
                return parsed_value

            except json.JSONDecodeError:
                raise serializers.ValidationError(
                    "Định dạng JSON không hợp lệ. Vui lòng kiểm tra lại dấu ngoặc, dấu phẩy hoặc dấu nháy kép."
                )
        if not isinstance(value, dict):
            raise serializers.ValidationError("Dữ liệu phải là một JSON Object hợp lệ.")
        return value

    def validate(self, attrs):
        chosen_plan = attrs.get("plan", self.fields["plan"].default)
        plan_config = PLAN_LIMITS.get(chosen_plan, PLAN_LIMITS[PLAN_STANDARD])

        for field in ["max_branches", "max_vehicles", "max_users"]:
            user_value = attrs.get(field)
            max_allowed = plan_config[field]

            if user_value is None:
                attrs[field] = max_allowed
            else:
                if user_value <= 0:
                    raise serializers.ValidationError(
                        {field: "Giá trị cấu hình phải lớn hơn 0."}
                    )
                if user_value > max_allowed:
                    raise serializers.ValidationError(
                        {
                            field: f"Gói {chosen_plan} chỉ cho phép cấu hình tối đa {max_allowed}. "
                            f"Bạn không thể thiết lập {user_value}."
                        }
                    )

        started_at = attrs.get("subscription_started_at")
        expires_at = attrs.get("subscription_expires_at")

        if started_at and expires_at and started_at >= expires_at:
            raise serializers.ValidationError(
                {"subscription_expires_at": "Ngày kết thúc phải lớn hơn ngày bắt đầu."}
            )

        return attrs
