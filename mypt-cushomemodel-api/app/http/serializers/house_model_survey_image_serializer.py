import json

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from app.core.helpers import global_variable as gb
from app.core.helpers.my_datetime import getFormatDatetimeNow
from app.http.models.house_model_survey_image import HouseModelSurveyImage


class HouseModelSurveyImageSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False, read_only=True)
    modelSurveyId = serializers.IntegerField(required=True, allow_null=False, source='model_survey_id', error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='ID khảo sát'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='ID khảo sát'),
    })
    floors = serializers.IntegerField(required=False)
    floor = serializers.IntegerField(required=True, allow_null=False, source='house_floor', error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='số tầng'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='số tầng'),
        'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='số tầng')
    })
    size = serializers.DictField(required=True, allow_null=False, allow_empty=False, source='house_size',
                                 error_messages={
                                     'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='diện tích'),
                                     'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='diện tích'),
                                     'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='diện tích'),
                                     'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='diện tích'),
                                     'empty': gb.TXT_ERROR_MESSAGE_FORMAT['empty'].format(item='thiết bị'),
                                 })
    devices = serializers.ListField(required=True, allow_null=False, allow_empty=True, source='tx_devices_info',
                                    error_messages={
                                        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='thiết bị'),
                                        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='thiết bị'),
                                        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='thiết bị'),
                                        'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='thiết bị')
                                    })
    sketches = serializers.ListField(required=True, allow_null=False, allow_empty=True, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='ảnh vẽ'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='ảnh vẽ'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='ảnh vẽ'),
        'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='ảnh vẽ')
    })
    sketchesType = serializers.CharField(required=True, allow_null=False, source='sketches_type', error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='loại ảnh vẽ'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='loại ảnh vẽ'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='loại ảnh vẽ'),
    })
    statusUpdate = serializers.IntegerField(required=False, allow_null=True, source='status_update', error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='trạng thái'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='trạng thái'),
        'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='trạng thái')
    })
    appId = serializers.CharField(required=True, allow_null=False, allow_blank=False, source='app_id', error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='app ID'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='app ID'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='app ID')
    })
    sdkAccUsername = serializers.CharField(required=True, allow_null=False, allow_blank=False, source='sdk_acc_username', error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='username'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='username'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='username')
    })
    sdkUserId = serializers.CharField(required=True, allow_blank=False, allow_null=False, source='sdk_user_id',
                                      error_messages={
                                          'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='user ID'),
                                          'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='user ID'),
                                          'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='user ID')
                                      })
    createdAt = serializers.DateTimeField(source='created_at', required=False)

    class Meta:
        model = HouseModelSurveyImage
        fields = ['id', 'modelSurveyId', 'floors', 'floor', 'size', 'devices', 'sketches', 'sketchesType',
                  'statusUpdate', 'appId', 'sdkAccUsername', 'sdkUserId', 'createdAt']

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
            instance.house_size = json.loads(instance.house_size)
            instance.tx_devices_info = json.loads(instance.tx_devices_info)
            instance.sketches = json.loads(instance.sketches)
        except Exception as ex:
            print('Error/Loi convert HouseModelSurveyImageSerializer' + str(ex))
        representation = super().to_representation(instance)
        return representation

    def create(self, validated_data):
        if validated_data['house_floor'] <= validated_data['floors']:
            validated_data['status_updated'] = 1
            validated_data['created_at'] = getFormatDatetimeNow()
            validated_data['house_size'] = json.dumps(validated_data['house_size'])
            validated_data['tx_devices_info'] = json.dumps(validated_data['tx_devices_info'])
            validated_data['sketches'] = json.dumps(validated_data['sketches'])
            validated_data.pop('floors')
            instance = HouseModelSurveyImage.objects.create(**validated_data)
        else:
            raise serializers.ValidationError(f'Không thể tạo hình ảnh vẽ cho tầng {str(validated_data["house_floor"])}')
        return validated_data

    def validate_devices(self, data):
        key_info = ['id', 'name', 'powerWifi24', 'powerWifi5', 'location', 'type', 'modelType']
        for item in data:
            for key in key_info:
                if key not in item:
                    raise serializers.ValidationError(
                        gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='thiết bị') + ' ' + str(key))
                if key == 'type':
                    if item[key] not in ['router', 'access_point']:
                        raise serializers.ValidationError(
                            gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='thiết bị') + ' ' + str(key))
                if key == 'modelType':
                    if item[key] not in ['model', 'other']:
                        raise serializers.ValidationError(
                            gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='thiết bị') + ' ' + str(key))
        return data


class UpdateHouseModelSurveyImageSerializer(HouseModelSurveyImageSerializer):

    def create(self, validated_data):
        if validated_data['house_floor'] <= validated_data['floors']:
            instance = HouseModelSurveyImage.objects.filter(model_survey_id=validated_data['model_survey_id'],
                                                            house_floor=validated_data['house_floor'])
            if instance.exists():
                validated_data['status_updated'] = 1
                validated_data['created_at'] = getFormatDatetimeNow()
                validated_data['house_size'] = json.dumps(validated_data['house_size'])
                validated_data['tx_devices_info'] = json.dumps(validated_data['tx_devices_info'])
                validated_data['sketches'] = json.dumps(validated_data['sketches'])
                validated_data.pop('floors')
                instance.update(**validated_data)
            else:
                validated_data['status_updated'] = 1
                validated_data['created_at'] = getFormatDatetimeNow()
                validated_data['house_size'] = json.dumps(validated_data['house_size'])
                validated_data['tx_devices_info'] = json.dumps(validated_data['tx_devices_info'])
                validated_data['sketches'] = json.dumps(validated_data['sketches'])
                validated_data.pop('floors')
                create_instance = HouseModelSurveyImage.objects.create(**validated_data)
        else:
            raise serializers.ValidationError(f'Không thể tạo hình ảnh vẽ cho tầng {str(validated_data["house_floor"])}')
        return validated_data
