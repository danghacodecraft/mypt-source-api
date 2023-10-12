from rest_framework import serializers
from ..models.emp_checkin import *

class EmpCheckinSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='checkin_id')
    accountNameMBN = serializers.CharField(source='MBN_account_name')
    code = serializers.CharField(source='emp_code')
    checkinDate = serializers.DateField(source='get_checkin_date_format')
    checkinTime = serializers.CharField(source='checkin_time')
    checkinDay = serializers.CharField(source='checkin_day')
    checkinMonth = serializers.CharField(source='checkin_month')
    checkinYear = serializers.CharField(source='checkin_year')
    sheetTime = serializers.CharField(source='sheet_time')
    workdayFactor = serializers.FloatField(source='workday_factor')
    workdayConvert = serializers.FloatField(source='workday_convert')
    blockName = serializers.CharField(source='block_name')
    checkinSuccess = serializers.CharField(source='checkin_success')
    teamName = serializers.CharField(source='team_name')
    closeCase = serializers.IntegerField(source='close_case')
    coordinateOffice = serializers.CharField(source='coordinate_office')
    coordinateBlock = serializers.CharField(source='coordinate_block')
    blockDistance = serializers.IntegerField(source='block_distance')
    countAuto = serializers.IntegerField(source='count_auto')
    countResponse = serializers.IntegerField(source='count_response')
    # tooLate = serializers.IntegerField(source='too_late')
    confirmInfo = serializers.IntegerField(source='confirm')
    historyCoordinate = serializers.CharField(source='history_coordinate')
    deviceName = serializers.CharField(source='get_device_name_format')

    class Meta:
        model = EmpCheckin
        # fields = '__all__'
        fields = ['id', 'accountNameMBN', 'code', 'checkinDate', 'checkinTime', 'checkinDay', 'checkinMonth', 'checkinYear',
                  'sheetTime', 'workdayFactor', 'workdayConvert', 'blockName', 'checkinSuccess', 'teamName', 'closeCase',
                  'location','note', 'coordinateOffice', 'coordinateBlock', 'blockDistance', 'countAuto',
                  'countResponse', 'confirmInfo', 'historyCoordinate', 'deviceName']

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