from rest_framework import serializers

class NotificationValidator(serializers.Serializer):
    title = serializers.CharField(required=True)
    
class ServiceSendNoti(serializers.Serializer):
    email = serializers.EmailField(required=True)

class ListCodeValidate(serializers.Serializer):
    empCode = serializers.ListField(required=True)
    
class ListEmailValidate(serializers.Serializer):
    list_email = serializers.ListField(required=True)
    
class EmailValidate(serializers.Serializer):
    email = serializers.EmailField(required=True)