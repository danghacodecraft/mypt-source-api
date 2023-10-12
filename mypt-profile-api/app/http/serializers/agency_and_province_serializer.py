from rest_framework import serializers
from ..models.agency_and_province import *


class AgencyAndProvinceSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(required=False, format="%d/%m/%Y", allow_null=True, source='created_at')
    updateAt = serializers.DateTimeField(required=False, format="%d/%m/%Y", allow_null=True, source='update_at')

    def __init__(self, *args, **kwargs):

        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = AgencyAndProvince
        fields = ['agency', 'province', 'createdAt', 'updateAt']
