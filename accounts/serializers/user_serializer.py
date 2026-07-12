from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
    tenant_name = serializers.SerializerMethodField()
    username = serializers.CharField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
    phone = serializers.CharField(allow_null=True)
    avatar = serializers.CharField(allow_null=True)
    branch_id = serializers.IntegerField(allow_null=True)
    branch_name = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()
    must_change_password = serializers.BooleanField(required=False)
    password_expires_at = serializers.DateTimeField(allow_null=True, required=False)
    locked_until = serializers.DateTimeField(allow_null=True, required=False)
    last_login = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)

    def get_tenant_name(self, obj):
        tenant_id = getattr(obj, "tenant_id", None)
        if tenant_id:
            from tenants.models import Tenant
            tenant = Tenant.objects.filter(pk=tenant_id).first()
            return tenant.name if tenant else "-"
        return "-"

    def get_branch_name(self, obj):
        branch_id = getattr(obj, "branch_id", None)
        if branch_id:
            from branches.models import Branch
            branch = Branch.objects.filter(pk=branch_id).first()
            return branch.name if branch else "-"
        return "-"


class UserListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(min_value=1, max_value=200, default=20)
    offset = serializers.IntegerField(min_value=0, default=0)


class UserCreateSerializer(serializers.Serializer):
    tenant = serializers.IntegerField()
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=255)
    full_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(
        max_length=20, required=False, allow_null=True, allow_blank=True
    )
    avatar = serializers.CharField(
        max_length=500, required=False, allow_null=True, allow_blank=True
    )
    is_active = serializers.BooleanField(default=True)
    branch = serializers.IntegerField(required=False, allow_null=True)
    must_change_password = serializers.BooleanField(required=False, default=False)
    password_expires_at = serializers.DateTimeField(required=False, allow_null=True)
    locked_until = serializers.DateTimeField(required=False, allow_null=True)


class UserUpdateSerializer(serializers.Serializer):
    tenant = serializers.IntegerField(required=False, allow_null=True)
    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(max_length=254, required=False)
    full_name = serializers.CharField(max_length=255)
    phone = serializers.CharField(
        max_length=20, required=False, allow_null=True, allow_blank=True
    )
    avatar = serializers.CharField(
        max_length=500, required=False, allow_null=True, allow_blank=True
    )
    is_active = serializers.BooleanField(default=True)
    branch = serializers.IntegerField(required=False, allow_null=True)
    must_change_password = serializers.BooleanField(required=False, default=False)
    password_expires_at = serializers.DateTimeField(required=False, allow_null=True)
    locked_until = serializers.DateTimeField(required=False, allow_null=True)
