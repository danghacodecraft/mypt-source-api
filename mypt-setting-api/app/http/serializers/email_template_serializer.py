from rest_framework import serializers
from ..models.email_template import EmailTemplate

class EmailTemplateSerializer(serializers.ModelSerializer):
    id  = serializers.IntegerField(required=False)
    template_name = serializers.CharField(required=True)
    field_require = serializers.CharField(required=True)
    html = serializers.CharField(required=True)
    is_deleted = serializers.IntegerField(required=False)
    
    class Meta:
        model = EmailTemplate
        fields = '__all__'