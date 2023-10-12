from rest_framework import serializers
from ..models.checkin_location import CheckinLocation


class CheckinLocationSerializer(serializers.ModelSerializer):
    buildingOfficeId = serializers.CharField(source='building_office_id')
    buildingOfficeName = serializers.CharField(source='building_office_name')
    address = serializers.CharField()
    statusWorking = serializers.IntegerField(source='status_working')

    def __init__(self, *args, **kwargs):

        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = CheckinLocation
        fields = ['buildingOfficeId', 'buildingOfficeName',
                  'address', 'statusWorking']
