from rest_framework import serializers
from ..models.provinces_and_region import *


class ProvincesAndRegionSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(required=False, format="%d/%m/%Y", allow_null=True, source='created_at')
    updateAt = serializers.DateTimeField(required=False, format="%d/%m/%Y", allow_null=True, source='update_at')
    provinceName = serializers.CharField(required=False, source='province_name', allow_null=True, allow_blank=True)
    provinceCode = serializers.CharField(required=False, source='province_code', allow_null=True, allow_blank=True)
    parentDepart = serializers.CharField(required=False, source='parent_depart', allow_null=True, allow_blank=True)
    regionCode = serializers.CharField(required=False, source='region_code', allow_null=True, allow_blank=True)

    def __init__(self, *args, **kwargs):

        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = ProvincesAndRegion
        fields = ['provinceCode', 'provinceName', 'createdAt', 'updateAt', 'parentDepart', 'region', 'regionCode']
