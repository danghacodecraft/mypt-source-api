from rest_framework import serializers
from app.http.models.queue_task import QueueTask

class QueueTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueueTask
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "deleted_at"]
        
    id = serializers.CharField(required=True)
    eta = serializers.DateTimeField(allow_null=True, input_formats=["%Y-%m-%dT%H:%M:%S.%f%z"])
    expires = serializers.DateTimeField(allow_null=True, input_formats=["%Y-%m-%dT%H:%M:%S.%f%z"])
    
    def create(self, validated_data):
        return QueueTask.objects.update_or_create(
            id=validated_data.pop("id"),
            defaults={
                **validated_data
            }
        )