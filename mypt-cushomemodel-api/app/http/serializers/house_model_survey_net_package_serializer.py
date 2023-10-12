from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from app.core.helpers.utils import return_choice_name
from app.http.models.house_model_survey_net_package import SurveyNetPackage


class SurveyNetPackageSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False)
    modelSurveyId = serializers.IntegerField(required=True, allow_null=False,
                                             error_messages={
                                                 'required': 'ID khảo sát là bắt buộc!',
                                                 'null': 'Vui lòng chọn ID khảo sát!',
                                             }, source='model_survey_id')
    idPackage = serializers.CharField(required=True, allow_null=False,
                                      error_messages={
                                          'required': 'ID gói cước là bắt buộc!',
                                          'null': 'Vui lòng chọn ID gói cước!',
                                      }, source='id_package')
    name = serializers.CharField(required=True, allow_null=False, allow_blank=False,
                                 error_messages={
                                     'required': 'Tên gói cước là bắt buộc!',
                                     'null': 'Vui lòng chọn tên gói cước!',
                                     'blank': 'Tên gói cước không được rỗng!',
                                 })
    downloadSpeed = serializers.IntegerField(required=True, allow_null=False,
                                             error_messages={
                                                 'required': 'Tốc độ download là bắt buộc!',
                                                 'null': 'Vui lòng chọn tốc độ download!',
                                             }, source='download_speed')
    uploadSpeed = serializers.IntegerField(required=True, allow_null=False,
                                           error_messages={
                                               'required': 'Tốc độ upload là bắt buộc!',
                                               'null': 'Vui lòng chọn tốc độ upload!',
                                           }, source='upload_speed')
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
        model = SurveyNetPackage
        fields = ['id', 'modelSurveyId', 'idPackage', 'name', 'downloadSpeed', 'uploadSpeed', 'quantity',
                  'modelType']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['modelType'] = return_choice_name(representation['modelType'],
                                                         SurveyNetPackage.MODEL_TYPE_CHOICES)
        return representation

    def create(self, validated_data):
        # Loại bỏ trường 'id' khỏi 'validated_data'
        validated_data.pop('id', None)
        instance = SurveyNetPackage.objects.create(**validated_data)
        return validated_data

    def validate_modelType(self, modelType):
        if modelType not in [x for x in SurveyNetPackage.LIST_MODEL_TYPE.keys()]:
            raise serializers.ValidationError('Sai modelType rồi!')
        return modelType
