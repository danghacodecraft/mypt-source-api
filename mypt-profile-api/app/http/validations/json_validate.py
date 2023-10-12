from rest_framework import serializers

class CaseValidate(serializers.Serializer):
    case = serializers.ListField()
    
    def validate_case(self, value):
        if value == []:
            raise serializers.ValidationError("case is valid")
        return value