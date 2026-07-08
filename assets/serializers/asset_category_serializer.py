from rest_framework import serializers


class AssetCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
    name = serializers.CharField()
    created_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)


class AssetCategoryListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(min_value=1, max_value=200, default=20)
    offset = serializers.IntegerField(min_value=0, default=0)
