from rest_framework import serializers
from ..models.theme_model import ThemeManager

class ThemeManagerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ThemeManager
        
    id = serializers.IntegerField(required=False)
    theme_code = serializers.CharField(required=True)
    icon_app = serializers.CharField(required=True)
    theme_background = serializers.CharField(required=False)
    branch = serializers.CharField(required=False, default="ALL")
    start_date = serializers.DateTimeField(required=True)
    due_date = serializers.DateTimeField(required=False)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)