from rest_framework import serializers

class VerifyOTPValidator(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)