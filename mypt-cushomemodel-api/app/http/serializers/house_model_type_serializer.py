from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from ..models.house_model_type import HouseModelType
from core.helpers.utils import return_choice_name


class HouseModelTypeSerializer(ModelSerializer):
    modelType = serializers.ChoiceField(choices=HouseModelType.CHOICES, default=HouseModelType.MAIN,
                                        source='model_type')
    coveredArea = serializers.IntegerField(source='covered_area')
    groupTemplate = serializers.CharField(source='group_template')
    createdAt = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S')
    updatedAt = serializers.DateTimeField(source='updated_at', format='%Y-%m-%d %H:%M:%S')
    isActive = serializers.IntegerField(source='is_active')
    myptUserId = serializers.IntegerField(source='mypt_user_id')
    myptUserEmail = serializers.CharField(source='mypt_user_email')
    myptUserFullName = serializers.CharField(source='mypt_user_fullname')

    class Meta:
        model = HouseModelType
        fields = ['id', 'name', 'modelType', 'coveredArea', 'groupTemplate', 'createdAt', 'updatedAt', 'isActive',
                  'myptUserId', 'myptUserEmail', 'myptUserFullName', ]

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
        representation['name'] = representation['name'].capitalize()
        if 'modelType' in representation:
            representation['modelType'] = return_choice_name(instance.model_type, HouseModelType.CHOICES)
        return representation
