from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from ..models.internet_packages import InternetPackages
from core.helpers.utils import return_choice_name


class InternetPackagesSerializer(ModelSerializer):
    customerType = serializers.ChoiceField(choices=InternetPackages.CUSTOMER_TYPE_CHOICES,
                                           default=InternetPackages.CUSTOMER_TYPE_NONE,
                                           source='customer_type')
    downloadSpeed = serializers.IntegerField(source='download_speed')
    uploadSpeed = serializers.IntegerField(source='upload_speed')
    createdAt = serializers.DateTimeField(required=False, source='created_at', format='%Y-%m-%d %H:%M:%S')
    updatedAt = serializers.DateTimeField(required=False, source='updated_at', format='%Y-%m-%d %H:%M:%S')
    isActive = serializers.IntegerField(required=False, source='is_active')
    myptUserId = serializers.IntegerField(source='mypt_user_id')
    myptUserEmail = serializers.CharField(source='mypt_user_email')
    myptUserFullName = serializers.CharField(source='mypt_user_fullname')

    class Meta:
        model = InternetPackages
        fields = ['id', 'name', 'customerType', 'downloadSpeed', 'uploadSpeed', 'createdAt', 'updatedAt', 'isActive',
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
        if 'customerType' in representation:
            representation['customerType'] = return_choice_name(instance.customer_type,
                                                                InternetPackages.CUSTOMER_TYPE_CHOICES)
        return representation
