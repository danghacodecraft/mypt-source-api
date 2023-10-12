import json

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from app.http.models.house_model_survey import *


class HouseModelSurveySerializer(ModelSerializer):
    # id
    contractCode = serializers.CharField(source='contract_code')
    regions = serializers.CharField()
    branchFullName = serializers.CharField(source='branch_fullname')
    sdkUserId = serializers.IntegerField(source='sdk_user_id')
    appId = serializers.CharField(source='app_id')
    sdkAccUsername = serializers.CharField(source='sdk_acc_username')
    idType = serializers.IntegerField(source='id_type')
    modelType = serializers.CharField(source='model_type')
    customerType = serializers.CharField(source='customer_type')
    houseLength = serializers.FloatField(source='house_length')
    houseWidth = serializers.FloatField(source='house_width')
    # floors
    rowsPerFloor = serializers.IntegerField(source='rows_per_floor')
    roomsPerRow = serializers.IntegerField(source='rooms_per_row')
    peoplePerRoom = serializers.IntegerField(source='people_per_room')
    userWifi = serializers.IntegerField(source='user_wifi')
    userLAN = serializers.IntegerField(source='user_lan')
    userCamera = serializers.IntegerField(source='user_camera')
    luxPackageCheck = serializers.IntegerField(source='lux_package_check')
    uploadAlotCheck = serializers.IntegerField(source='upload_alot_check')
    concurrentUsageRate = serializers.FloatField(source='concurrent_usage_rate')
    otherCheck = serializers.IntegerField(source='other_check')
    otherWidth = serializers.FloatField(source='other_width')
    otherLength = serializers.FloatField(source='other_length')
    otherUserWifi = serializers.IntegerField(source='other_user_wifi')
    internetPackages = serializers.CharField(source='internet_packages')
    # routers
    accessPoints = serializers.CharField(source='access_points')
    totalAP = serializers.DictField(source='total_ap')
    conclusion = serializers.ListField()
    # reason
    isCurrent = serializers.IntegerField(source='is_current')
    createdAt = serializers.DateTimeField(source='created_at', format='%H:%M:%S %d/%m/%Y')

    class Meta:
        model = HouseModelSurvey
        fields = ['id', 'contractCode', 'regions', 'branchFullName', 'sdkUserId', 'appId', 'sdkAccUsername', 'idType',
                  'modelType', 'customerType', 'houseLength', 'houseWidth', 'floors', 'rowsPerFloor', 'roomsPerRow',
                  'peoplePerRoom', 'userWifi', 'userLAN', 'userCamera', 'luxPackageCheck', 'uploadAlotCheck',
                  'concurrentUsageRate', 'otherCheck', 'otherWidth', 'otherLength', 'otherUserWifi', 'internetPackages',
                  'routers', 'accessPoints', 'totalAP', 'isCurrent', 'conclusion', 'reason', 'createdAt']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        try:
            instance.total_ap = json.loads(instance.total_ap)
            instance.conclusion = json.loads(instance.conclusion)
        except Exception as ex:
            print('Error/Loi convert HouseModelSurveySerializer' + str(ex))
        representation = super().to_representation(instance)
        try:
            representation['internetPackages'] = json.loads(representation['internetPackages'])
            representation['routers'] = json.loads(representation['routers'])
            representation['accessPoints'] = json.loads(representation['accessPoints'])
        except Exception as ex:
            print('Error/Loi convert HouseModelSurveySerializer' + str(ex))
        return representation
