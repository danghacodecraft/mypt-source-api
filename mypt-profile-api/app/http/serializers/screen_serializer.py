from rest_framework import serializers
from ..models.screen import *

class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        # 'created_at','updated_at', deleted_at
        fields = ["id","group","email","created_at","updated_at","deleted_at"]