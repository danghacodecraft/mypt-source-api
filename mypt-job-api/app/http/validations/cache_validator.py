from rest_framework import serializers

class KeyValidate(serializers.Serializer):
    key = serializers.CharField(required=True, allow_blank=False, allow_null=True)