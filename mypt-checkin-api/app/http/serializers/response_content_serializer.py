from rest_framework import serializers
from ..models.response_content import *

class ResponseContentSerializer(serializers.ModelSerializer):
    idContent = serializers.IntegerField(source='id')
    contentResponse = serializers.CharField(source='content')

    class Meta:
        model = ResponseContent
        fields = ['idContent', 'contentResponse']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        foreignKey = kwargs.pop('foreignKey', None)

        super().__init__(*args, **kwargs)

        # if history_contact:
        #     self.fields['history_contact'] = HistoryContactSerializer(many=True)


        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if foreignKey is not None:
            self.fields.pop(foreignKey)