from ..models.improved_car import *
from rest_framework import serializers
from ...configs.variable import *

class ImprovedCarValidate(serializers.Serializer):
    nameImprovedCar = serializers.CharField(required=True)
    currentStatus = serializers.CharField(required=True)
    purpose = serializers.CharField(required=True)
    solution = serializers.CharField(required=True)
    typeTitle = serializers.IntegerField(required=True)
        
class EvaluateIdeaValidate(serializers.Serializer):
    idPost = serializers.IntegerField(required=True)
    effective = serializers.CharField(required=True)
    creative = serializers.CharField(required=True)
    possibility = serializers.CharField(required=True)
    note = serializers.CharField(required=True)
    
class CommentVaidate(serializers.Serializer):
    idTree = serializers.IntegerField(required=True)
    parent = serializers.CharField(required=True)
    msg = serializers.CharField(required=True)
    level = serializers.CharField(required=True)
    
class LikeValidate(serializers.Serializer):
    id = serializers.CharField(required=True)
    
class PostRateValidate(serializers.Serializer):
    idTree = serializers.IntegerField()
    rate = serializers.IntegerField()
    
    def validate_rate(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Số sao truyền lên không hợp lệ!")
        return value
    
    def validate_idTree(self, value):
        if not ImprovedCar.objects.filter(id=value, process_status='publish').exists():
            raise serializers.ValidationError(ERROR['BLOG_NOT_EXISTS'])
        return value
    