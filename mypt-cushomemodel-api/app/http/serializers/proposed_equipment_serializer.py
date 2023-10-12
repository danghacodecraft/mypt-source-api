from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from ..models.proposed_equipment import ProposedEquipment
from ...core.helpers.my_datetime import getFormatDatetimeNow
from ...core.helpers.utils import return_choice_name, return_choice_id_or_code


class ProposedEquipmentSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=False)
    name = serializers.CharField(required=True, allow_null=False, allow_blank=False, source='parent_name')
    modemRule = serializers.CharField(required=True, allow_null=False, allow_blank=False, source='modem_rule')
    LANWifi = serializers.IntegerField(required=True, allow_null=False, source='lan_wifi')
    wifi = serializers.IntegerField(required=True, allow_null=False)
    quantityWAN = serializers.IntegerField(required=False, allow_null=False, source='quantity_wan')
    wifi24Pow = serializers.IntegerField(required=False, allow_null=True, source='wifi_24_ghz')
    wifi5Pow = serializers.IntegerField(required=False, allow_null=True, source='wifi_5_ghz')
    deviceOrigin = serializers.CharField(required=True, allow_null=False, allow_blank=False, source='device_origin')
    createdAt = serializers.DateTimeField(required=False, allow_null=False, source='created_at')
    updatedAt = serializers.DateTimeField(required=False, allow_null=False, source='created_at')
    isActive = serializers.IntegerField(required=False, source='is_active')
    sdkUserId = serializers.IntegerField(required=True, allow_null=False, source='sdk_user_id')
    sdkAccUsername = serializers.CharField(required=True, allow_null=False, allow_blank=False,
                                           source='sdk_acc_username')

    class Meta:
        model = ProposedEquipment
        fields = ['id', 'name', 'modemRule', 'LANWifi', 'wifi', 'quantityWAN', 'wifi24Pow', 'wifi5Pow', 'deviceOrigin',
                  'createdAt', 'updatedAt', 'isActive', 'sdkUserId', 'sdkAccUsername']

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
        try:
            representation['modemRule'] = return_choice_name(representation['modemRule'],
                                                             ProposedEquipment.MODEM_RULE_CHOICES)
            representation['deviceOrigin'] = return_choice_name(representation['deviceOrigin'],
                                                                ProposedEquipment.DEVICE_ORIGIN_CHOICES)
            representation['isActive'] = return_choice_name(representation['isActive'],
                                                            ProposedEquipment.STATUS_ACTIVE_CHOICES)
        except Exception as ex:
            print(f'Error/Loi: {ex}')
        return representation

    def create(self, validated_data):
        validated_data['created_at'] = getFormatDatetimeNow()
        validated_data['quantity_wan'] = 0
        validated_data['wifi_24_ghz'] = None
        validated_data['wifi_5_ghz'] = None
        validated_data['is_active'] = ProposedEquipment.IS_ACTIVE
        validated_data['modem_rule'] = return_choice_id_or_code(validated_data['modem_rule'],
                                                                ProposedEquipment.MODEM_RULE_CHOICES)
        validated_data['device_origin'] = return_choice_id_or_code(validated_data['device_origin'],
                                                                   ProposedEquipment.DEVICE_ORIGIN_CHOICES)
        instance = ProposedEquipment.objects.create(**validated_data)
        return validated_data

    def validate_modemRule(self, value):
        if value.lower() not in [item.lower() for item in ProposedEquipment.LIST_MODEM_RULE_TYPES.values()]:
            raise serializers.ValidationError(f'Invalid modemRule: {value}')
        return value

    def validate_deviceOrigin(self, value):
        if value.lower() not in [item.lower() for item in ProposedEquipment.LIST_DEVICE_ORIGIN.values()]:
            raise serializers.ValidationError(f'Invalid deviceOrigin: {value}')
        return value
