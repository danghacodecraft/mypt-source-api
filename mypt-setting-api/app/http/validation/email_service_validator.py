from rest_framework import serializers

class EmailServiceValidation(serializers.Serializer):
    subject = serializers.CharField(required=True)
    template_name = serializers.CharField(required=True)
    to = serializers.ListField(required=True)
    content_fields = serializers.DictField(required=True)
    cc = serializers.ListField(required=False)
    bcc = serializers.ListField(required=False)
    ignore_error = serializers.BooleanField(required=True)
    
class EmailWithTemplateServiceValidation(serializers.Serializer):
    subject = serializers.CharField(required=True)
    template = serializers.CharField(required=True)
    to = serializers.ListField(required=True)
    content_fields = serializers.DictField(required=True)
    cc = serializers.ListField(required=False, default=[])
    bcc = serializers.ListField(required=False, default=[])
    
class EmailContentFieldValidator(serializers.Serializer):
    images = serializers.ListField(required=False)
    
class ImageAttachValidator(serializers.Serializer):
    name_in_html = serializers.CharField(required=True)
    image_url = serializers.CharField(required=True)
    attach_type = serializers.CharField(required=True)