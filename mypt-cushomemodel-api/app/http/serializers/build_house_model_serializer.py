import json

from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from ..models.build_house_model import BuildHouseModel
from ..validation.simulate_wifi_image_validation import SimulateWifiImageValidate
from ...core.helpers.my_datetime import getFormatDatetimeNow


class BuildHouseModelSerializer(ModelSerializer):
    modelSurveyId = serializers.IntegerField(source='model_survey_id')
    houseFloor = serializers.IntegerField(source='house_floor')
    houseWidth = serializers.IntegerField(source='house_width')
    houseLength = serializers.IntegerField(source='house_length')
    txLocation = serializers.CharField(source='tx_location')
    txPower = serializers.CharField(source='tx_power')
    txName = serializers.CharField(source='tx_name')
    wallAttenuation = serializers.IntegerField(source='wall_attenuation')
    wallAttenuationInfo = serializers.CharField(source='wall_attenuation_info')
    imageShape = serializers.CharField(source='image_shape')
    image = serializers.CharField(source='image_link_original')
    wifi24Image = serializers.CharField(source='image_link_wifi24')
    wifi5Image = serializers.CharField(source='image_link_wifi5')
    # statusUpdated = serializers.IntegerField(source='status_updated')
    imageType = serializers.CharField(source='image_type')
    size = serializers.CharField()
    sketches = serializers.CharField()
    devices = serializers.CharField()

    class Meta:
        model = BuildHouseModel
        fields = ['modelSurveyId', 'houseFloor', 'houseWidth', 'houseLength', 'txLocation',
                  'txPower', 'txName', 'wallAttenuation', 'wallAttenuationInfo', 'imageShape', 'corners', 'edges',
                  'image', 'wifi24Image', 'wifi5Image', 'imageType', 'size', 'sketches', 'devices']

    def to_representation(self, instance):
        try:
            instance.tx_location = eval(instance.tx_location)
            instance.tx_power = eval(instance.tx_power)
            instance.tx_name = json.loads(instance.tx_name)
            instance.wall_attenuation_info = json.loads(instance.wall_attenuation_info)
            instance.image_shape = json.loads(instance.image_shape)
            instance.corners = json.loads(instance.corners)
            instance.edges = json.loads(instance.edges)
        except Exception as ex:
            print('Error/Loi: ', str(ex))
        representation = super().to_representation(instance)
        return representation


class CreateBuildHouseModelSerializer(SimulateWifiImageValidate):
    modelSurveyId = serializers.IntegerField()
    txLocation = serializers.ListField(required=True,
                                       allow_null=False,
                                       allow_empty=True,
                                       error_messages={
                                           'required': 'Vị trị các thiết bị là bắt buộc!',
                                           'null': 'Vị trị các thiết bị không được là giá trị null',
                                           'empty': 'Vị trị các thiết bị không được rỗng!',
                                       })
    txPower = serializers.ListField(required=True,
                                    allow_null=False,
                                    allow_empty=True,
                                    error_messages={
                                        'required': 'Vị trị các thiết bị là bắt buộc!',
                                        'null': 'Vị trị các thiết bị không được là giá trị null',
                                        'empty': 'Vị trị các thiết bị không được rỗng!',
                                    })
    txName = serializers.ListField(required=True,
                                   allow_null=False,
                                   allow_empty=True,
                                   error_messages={
                                       'required': 'Tên các thiết bị là bắt buộc!',
                                       'null': 'Tên các thiết bị không được là giá trị null',
                                       'empty': 'Tên các thiết bị không được rỗng!',
                                   })
    wallAttenuation = serializers.IntegerField(required=True, allow_null=False,
                                               error_messages={
                                                   'required': 'Thông tin vật cản là bắt buộc!',
                                                   'null': 'Vui lòng chọn thông tin vật cản!'
                                               })
    wallAttenuationInfo = serializers.DictField(required=True, allow_null=False,
                                                error_messages={
                                                    'required': 'Thông tin vật cản là bắt buộc!',
                                                    'null': 'Vui lòng chọn thông tin vật cản!',
                                                })
    image = serializers.CharField()
    wifi24Image = serializers.CharField(allow_blank=False, allow_null=True)
    wifi5Image = serializers.CharField(allow_blank=False, allow_null=True)

    def create(self, validated_data):
        build_model = BuildHouseModel.objects.create(
            model_survey_id=validated_data['modelSurveyId'],
            house_floor=validated_data['houseFloor'],
            house_width=validated_data['houseWidth'],
            house_length=validated_data['houseLength'],
            tx_location=json.dumps(validated_data['txLocation']),
            tx_power=validated_data['txPower'],
            tx_name=json.dumps(validated_data['txName']),
            wall_attenuation=validated_data['wallAttenuation'],
            wall_attenuation_info=json.dumps(validated_data['wallAttenuationInfo']),
            image_shape=json.dumps(validated_data['imageShape']),
            corners=json.dumps(validated_data['corners']),
            edges=json.dumps(validated_data['edges']),
            image_link_original=validated_data['image'],
            image_link_wifi24=validated_data['wifi24Image'],
            image_link_wifi5=validated_data['wifi5Image'],
            status_updated=1,
            created_at=getFormatDatetimeNow()
        )
        return build_model


class UpdateBuildHouseModelSerializer(CreateBuildHouseModelSerializer):
    def create(self, validated_data):
        build_model = BuildHouseModel.objects.filter(model_survey_id=validated_data['modelSurveyId'],
                                                     house_floor=validated_data['houseFloor'])
        build_model.update(
            model_survey_id=validated_data['modelSurveyId'],
            house_width=validated_data['houseWidth'],
            house_length=validated_data['houseLength'],
            tx_location=json.dumps(validated_data['txLocation']),
            tx_power=validated_data['txPower'],
            tx_name=json.dumps(validated_data['txName']),
            wall_attenuation=validated_data['wallAttenuation'],
            wall_attenuation_info=json.dumps(validated_data['wallAttenuationInfo']),
            image_shape=json.dumps(validated_data['imageShape']),
            corners=json.dumps(validated_data['corners']),
            edges=json.dumps(validated_data['edges']),
            image_link_original=validated_data['image'],
            image_link_wifi24=validated_data['wifi24Image'],
            image_link_wifi5=validated_data['wifi5Image'],
            created_at=getFormatDatetimeNow()
        )
        return build_model
