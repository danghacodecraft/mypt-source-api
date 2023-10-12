from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from app.core.helpers.utils import return_choice_name
from app.http.models.house_model_survey_equipment import SurveyEquipments
from app.http.models.house_model_survey_net_package import SurveyNetPackage


class SurveyEquipmentSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False)
    modelSurveyId = serializers.IntegerField(required=True, allow_null=False,
                                             error_messages={
                                                 'required': 'ID khảo sát là bắt buộc!',
                                                 'null': 'Vui lòng chọn ID khảo sát!',
                                             }, source='model_survey_id')
    idEquipment = serializers.CharField(required=True, allow_null=False,
                                        error_messages={
                                            'required': 'ID thiết bị là bắt buộc!',
                                            'null': 'Vui lòng chọn ID thiết bị!',
                                        }, source='id_equipment')
    name = serializers.CharField(required=True, allow_null=False, allow_blank=False,
                                 error_messages={
                                     'required': 'Tên thiết bị là bắt buộc!',
                                     'null': 'Vui lòng chọn tên thiết bị!',
                                     'blank': 'Tên thiết bị không được rỗng!',
                                 }, source='parent_name')
    modemRule = serializers.CharField(required=True, allow_null=False, allow_blank=False,
                                      error_messages={
                                          'required': 'Chức năng thiết bị là bắt buộc!',
                                          'null': 'Vui lòng chọn chức năng thiết bị!',
                                          'blank': 'Chức năng thiết bị không được rỗng!',
                                      }, source='modem_rule')
    LANWifi = serializers.IntegerField(required=True, allow_null=False,
                                       error_messages={
                                           'required': 'Số lượng tối đa LANWifi là bắt buộc!',
                                           'null': 'Vui lòng chọn số lượng tối đa LANWifi!'
                                       }, source='lan_wifi')
    wifi = serializers.IntegerField(required=True, allow_null=False,
                                    error_messages={
                                        'required': 'Số lượng user wifi là bắt buộc!',
                                        'null': 'Vui lòng chọn số lượng user wifi!'
                                    })
    wifi24Pow = serializers.IntegerField(required=True, allow_null=True,
                                         error_messages={
                                             'required': 'Công suất wifi 2.4 là bắt buộc!',
                                         }, source='wifi_24_ghz')
    wifi5Pow = serializers.IntegerField(required=True, allow_null=True,
                                        error_messages={
                                            'required': 'Tốc độ upload là bắt buộc!',
                                        }, source='wifi_5_ghz')
    quantity = serializers.IntegerField(required=True, allow_null=False,
                                        error_messages={
                                            'required': 'Số lượng gói cước là bắt buộc!',
                                            'null': 'Vui lòng chọn số lượng gói cước!'
                                        })
    modelType = serializers.CharField(required=True, allow_null=False, allow_blank=False,
                                      error_messages={
                                          'required': 'Gói cước thuộc mô hình nào là bắt buộc!',
                                          'null': 'Vui lòng chọn gói cước thuộc mô hình nào!',
                                          'blank': 'Gói cước thuộc mô hình nào không được rỗng!',
                                      }, source='model_type')

    class Meta:
        model = SurveyEquipments
        fields = ['id', 'modelSurveyId', 'idEquipment', 'name', 'modemRule', 'LANWifi', 'wifi', 'wifi24Pow', 'wifi5Pow',
                  'quantity', 'modelType']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        instance.modem_rule = return_choice_name(instance.modem_rule, SurveyEquipments.MODEM_RULE_CHOICES)
        representation = super().to_representation(instance)
        return representation

    def create(self, validated_data):
        # Loại bỏ trường 'id' khỏi 'validated_data'
        validated_data.pop('id', None)
        instance = SurveyEquipments.objects.create(**validated_data)
        return validated_data

    def validate_modemRule(self, modemRule):
        if modemRule not in [x for x in SurveyEquipments.LIST_MODEM_RULE.keys()]:
            raise serializers.ValidationError('Sai modemRule rồi!')
        return modemRule

    def validate_modelType(self, modelType):
        if modelType not in [x for x in SurveyEquipments.LIST_MODEL_TYPE.keys()]:
            raise serializers.ValidationError('Sai modelType rồi!')
        return modelType
