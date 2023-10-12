import json

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from app.core.helpers.my_datetime import getFormatDatetimeNow
from app.http.models.current_contract_info_log import CurrentContractInfoLog


class CurrentContractInfoLogSerializer(ModelSerializer):
    # id
    contractCode = serializers.CharField(source='contract_code')
    regions = serializers.CharField()
    branchFullName = serializers.CharField(source='branch_fullname')
    routers = serializers.ListField()
    accessPoints = serializers.ListField(source='access_points')
    internetPackages = serializers.ListField(source='internet_packages')
    totalAP = serializers.IntegerField(source='total_ap')
    sdkUserId = serializers.IntegerField(source='sdk_user_id')
    appId = serializers.CharField(source='app_id')
    sdkAccUsername = serializers.CharField(source='sdk_acc_username')
    createdAt = serializers.DateTimeField(required=False, source='created_at')
    updatedAt = serializers.DateTimeField(required=False, source='updated_at')

    class Meta:
        model = CurrentContractInfoLog
        fields = ['contractCode', 'regions', 'branchFullName', 'routers', 'accessPoints', 'internetPackages',
                  'totalAP', 'sdkUserId', 'sdkAccUsername', 'appId', 'createdAt', 'updatedAt']

    def to_representation(self, instance):
        try:
            instance.routers = json.loads(instance.routers)
            instance.access_points = json.loads(instance.access_points)
            instance.internet_packages = json.loads(instance.internet_packages)
        except Exception as ex:
            print('Error/Loi: ', str(ex))
            pass
        representation = super().to_representation(instance)
        return representation

    def create(self, validated_data):
        validated_data['routers'] = json.dumps(validated_data['routers'])
        validated_data['access_points'] = json.dumps(validated_data['access_points'])
        validated_data['internet_packages'] = json.dumps(validated_data['internet_packages'])
        validated_data['created_at'] = getFormatDatetimeNow()
        instance = CurrentContractInfoLog.objects.create(**validated_data)
        return validated_data
