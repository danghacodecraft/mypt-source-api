from rest_framework import serializers
from ..models.email_schedule_information import EmailScheduleInformation

class EmailScheduleInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailScheduleInformation
        fields = '__all__'
        
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False)
    input_data = serializers.CharField(required=True)
    is_done = serializers.BooleanField(required=False)
    