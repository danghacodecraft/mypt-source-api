from rest_framework import serializers
from ..models.tools import Tools
from ...configs.maps_key import TOOLS_DB, TOOLS_DEFAULT_VALUE

class ToolSerializer(serializers.ModelSerializer):
    
    start_date = serializers.DateField(required=False, format="%d/%m/%Y", allow_null=True)
    expire_date = serializers.DateField(required=False, format="%d/%m/%Y", allow_null=True)
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        status_message = kwargs.pop('status_message', False)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
        for key, value in TOOLS_DB.items():
            if key != value:
                self.fields[key] = self.fields[value]
        if status_message:
            self.fields['status'] = serializers.CharField()
            self.fields['keyStatus'] = serializers.CharField(source="key_status")
            
    def to_representation(self, instance):
        _repre = super().to_representation(instance).copy()
        try:
            [_repre.update({item: _repre[item] if _repre[item] is not None else TOOLS_DEFAULT_VALUE[item]}) for item in list(_repre.keys())]
            _repre["stockName"] = [_repre.get("stockName")]
        except Exception as e:
            return _repre
        return _repre
    
    def create(self, validated_data):
        Tools.objects.update_or_create(
            scm_id=validated_data.get('scm_id', None),
            defaults=validated_data
        )
        return validated_data
        
        
    class Meta:
        model = Tools
        fields = list(TOOLS_DB.values())
        
