from rest_framework import serializers
from ..models.emp_checkin_history import *

class empCheckinHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='history_id')
    checkin_id = serializers.CharField(source="checkin_id")
    coordinate = serializers.CharField(source='coordinate')
    updateTime = serializers.DateTimeField(source='update_time')
    status = serializers.IntegerField()
    typeCheckin = serializers.CharField(source='type_checkin')
    code = serializers.CharField(source='emp_code')
    checkinDate = serializers.DateField(source='checkin_date')


    class Meta:
        model = empCheckinHistory
        # fields = '__all__'
        fields = ['id', 'checkin_id', 'coordinate', 'updateTime', 'status', 'typeCheckin' , 'code', 'checkinDate']

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