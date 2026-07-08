from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    full_name = serializers.CharField()
    phone = serializers.CharField(allow_null=True)
    avatar = serializers.CharField(allow_null=True)
    branch_id = serializers.IntegerField(allow_null=True)
    is_active = serializers.BooleanField()
    last_login = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)


class UserListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(min_value=1, max_value=200, default=20)
    offset = serializers.IntegerField(min_value=0, default=0)
