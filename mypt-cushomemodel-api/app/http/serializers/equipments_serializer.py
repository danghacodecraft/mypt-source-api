from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from ..models.equipments import Equipments
from core.helpers.utils import return_choice_name


class EquipmentsSerializer(ModelSerializer):
    name = serializers.CharField(source='parent_name')
    codeID = serializers.IntegerField(source='code_id')
    LANWifi = serializers.IntegerField(source='lan_wifi')
    modemRule = serializers.ChoiceField(choices=Equipments.MODEM_RULE_CHOICES, source='modem_rule')
    quantityWAN = serializers.IntegerField(source='quantity_wan')
    wifi24Pow = serializers.IntegerField(source='wifi_24_ghz')
    wifi5Pow = serializers.IntegerField(source='wifi_5_ghz')
    createdAt = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S')
    updatedAt = serializers.DateTimeField(source='updated_at', format='%Y-%m-%d %H:%M:%S')
    isActive = serializers.IntegerField(source='is_active')
    myptUserId = serializers.IntegerField(source='mypt_user_id')
    myptUserEmail = serializers.CharField(source='mypt_user_email')
    myptUserFullName = serializers.CharField(source='mypt_user_fullname')

    class Meta:
        model = Equipments
        fields = ['id', 'name', 'codeID', 'LANWifi', 'wifi', 'modemRule', 'quantityWAN', 'wifi24Pow', 'wifi5Pow',
                  'createdAt', 'updatedAt', 'isActive',
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
        if 'modemRule' in representation:
            representation['modemRule'] = return_choice_name(instance.modem_rule, Equipments.MODEM_RULE_CHOICES)

        # representation['myptUserFullName'] = representation['myptUserFullName'].title()
        return representation
