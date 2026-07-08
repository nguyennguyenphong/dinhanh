from rest_framework import serializers


class AssetResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
    category_id = serializers.IntegerField(allow_null=True)
    branch_id = serializers.IntegerField(allow_null=True)
    assigned_to_id = serializers.IntegerField(allow_null=True)
    code = serializers.CharField()
    name = serializers.CharField()
    serial_number = serializers.CharField(allow_null=True)
    purchase_date = serializers.DateField(allow_null=True)
    purchase_price = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    depreciation_rate = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    current_value = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    warranty_expiry = serializers.DateField(allow_null=True)
    status = serializers.CharField()
    notes = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)
