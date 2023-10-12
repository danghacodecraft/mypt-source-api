from rest_framework import serializers
from ..models.emp_response import *

class EmpResponseSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(source='id')
    empCode = serializers.CharField(source='emp_code')
    updateTime = serializers.CharField(source='get_update_time_format')
    responseContent = serializers.CharField(source='response')
    responseId = serializers.IntegerField(source='response_id')
    checkinId = serializers.IntegerField(source='checkin_id')
    deviceId = serializers.CharField(source='device_id')

    class Meta:
        model = EmpResponse
        fields = ['id', 'empCode', 'updateTime', 'responseContent', 'responseId', 'coordinate', 'checkinId', 'deviceId']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        foreignKey = kwargs.pop('foreignKey', None)

        super().__init__(*args, **kwargs)

        # if history_contact:
        #     self.fields['history_contact'] = HistoryContactSerializer(many=True)


        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if foreignKey is not None:
            self.fields.pop(foreignKey)