from rest_framework import serializers
from ..models.account_management_tb import *

class AccountManagemenSerializer(serializers.ModelSerializer):

    accountNameMBN = serializers.CharField(source='MBN_account_name')
    code = serializers.CharField(source='emp_code')
    blockName = serializers.CharField(source='block_name')
    deviceId = serializers.CharField(source='device_id')
    coordinateOffice = serializers.CharField(source='toa_do_van_phong')
    coordinateWarehouse = serializers.CharField(source='toa_do_kho')
    coordinateWorking = serializers.CharField(source='toa_do_lam_viec')
    workingRadius = serializers.FloatField(source='ban_kinh_lam_viec')
    activeTime = serializers.CharField(source='acctive_time')
    deviceIdMypt = serializers.CharField(source='device_id_mypt')
    deviceName = serializers.CharField(source='device_name')
    deviceModel = serializers.CharField(source='device_model')
    deviceToken = serializers.CharField(source='device_token')

    class Meta:
        model = AccountManagement
        # fields = '__all__'
        fields = ['accountNameMBN', 'code', 'blockName', 'deviceId', 'coordinateOffice', 'coordinateWarehouse',
                  'coordinateWorking', 'workingRadius', 'activeTime', 'deviceIdMypt', 'deviceName' , 'deviceModel', 'deviceToken']

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


