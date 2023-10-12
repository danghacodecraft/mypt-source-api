from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from ..models.material_loss import MaterialLoss


class MaterialLossSerializer(ModelSerializer):
    colorCode = serializers.CharField(required=True, source='color_code')
    createdAt = serializers.DateTimeField(required=False, source='created_at', format='%Y-%m-%d %H:%M:%S')
    updatedAt = serializers.DateTimeField(required=False, source='updated_at', format='%Y-%m-%d %H:%M:%S')
    isActive = serializers.IntegerField(required=False, source='is_active')
    myptUserId = serializers.IntegerField(source='mypt_user_id')
    myptUserEmail = serializers.CharField(source='mypt_user_email')
    myptUserFullName = serializers.CharField(source='mypt_user_fullname')

    class Meta:
        model = MaterialLoss
        fields = ['id', 'name', 'loss', 'image', 'colorCode', 'createdAt', 'updatedAt', 'isActive',
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
        # representation['myptUserFullName'] = representation['myptUserFullName'].title()
        return representation
