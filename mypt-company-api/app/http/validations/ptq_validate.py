from ..models.improved_car import *
from rest_framework import serializers
from ...configs.variable import *

class MonthValidate(serializers.Serializer):
    month = serializers.IntegerField()
    
    def validate_month(self, value):
        if value == 0:
            raise serializers.ValidationError("Bỏ qua month")
        return value
    
class DateValidate(serializers.Serializer):
    dateStart = serializers.DateField(format="%Y-%m-%d")
    dateEnd = serializers.DateField(format="%Y-%m-%d")
    
class ListTypeValidate(serializers.Serializer):
    typeId = serializers.ListField()
    
    def validate_typeId(self, value):
        if value == []:
            raise serializers.ValidationError("typeId không có dữ liệu []")
        return value
    
class IdValidate(serializers.Serializer):
    id = serializers.IntegerField()
    
class ExplanationValidate(serializers.Serializer):
    id = serializers.IntegerField()
    content = serializers.CharField()