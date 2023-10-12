from email.policy import default
from ..models.ptq import *
from rest_framework import serializers
from ...configs.variable import *

class PtqSerializer(serializers.ModelSerializer):
    region = serializers.CharField(required=False, allow_null=True)
    partner = serializers.CharField(required=False, allow_null=True)
    blockName = serializers.CharField(source="block_name", required=False, allow_null=True)
    empName = serializers.CharField(source="emp_name", required=False, allow_null=True)
    contract = serializers.CharField(required=False, allow_null=True)
    errorType = serializers.CharField(source="error_type", required=False, allow_null=True)
    dateComplete = serializers.DateTimeField(format=DATETIME_FORMAT ,source="date_complete", required=False, allow_null=True)
    errorMain = serializers.CharField(source="error_main", required=False, allow_null=True)
    errorGroup = serializers.CharField(source="error_group", required=False, allow_null=True)
    errorDescription = serializers.CharField(source="error_description", required=False, allow_null=True)
    errorDetail = serializers.CharField(source="error_detail", required=False, allow_null=True)
    punishment = serializers.IntegerField(required=False, allow_null=True)
    accountMbn = serializers.CharField(source="account_mbn", required=False, allow_null=True)
    dateCheck = serializers.DateField(format=DATE_FORMAT, source="date_check", required=False, allow_null=True)
    email = serializers.CharField(required=False, allow_null=True)
    errorNumber = serializers.IntegerField(source="error_number", required=False, allow_null=True)
    deadline = serializers.DateField(format=DATE_FORMAT, required=False, allow_null=True)
    recorded = serializers.IntegerField(required=False, allow_null=True)
    recordedName = serializers.CharField(required=False, allow_null=True, source="get_type")
    recordedType = serializers.CharField(required=False, allow_null=True, source="get_key_type")
    note = serializers.CharField(required=False, allow_null=True)
    thematic = serializers.CharField(required=False, allow_null=True)
    isRead = serializers.BooleanField(source="is_read", required=False, allow_null=True)
    updatedBy = serializers.CharField(source="updated_by", required=False, allow_null=True)
    createdAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="created_at", required=False, allow_null=True)
    updatedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="updated_at", required=False, allow_null=True)
    deletedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="deleted_at", required=False, allow_null=True)
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        not_fields = kwargs.pop('not_fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        if not_fields is not None:
            for field_name in not_fields:
                self.fields.pop(field_name)
                    
    class Meta:
        model = Ptq
        fields = [
            "id","region","partner","blockName","empName","contract",
            "errorType","dateComplete","errorMain","errorGroup",
            "errorDescription","errorDetail","punishment",
            "accountMbn","dateCheck","email","errorNumber",
            "deadline","recorded","note","thematic","updatedBy",
            "createdAt","updatedAt","deletedAt","isRead","recordedName","recordedType"
        ]
        
class PtqHistorySerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    content = serializers.CharField(required=False, allow_null=True)
    ptqId = serializers.IntegerField(source="ptq_id", required=False, allow_null=True)
    feedback = serializers.CharField(required=False, allow_null=True)
    times = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.IntegerField(required=False, allow_null=True)
    recordedName = serializers.CharField(required=False, allow_null=True, source="get_type")
    createdAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="created_at", required=False, allow_null=True)
    updatedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="updated_at", required=False, allow_null=True)
    deletedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="deleted_at", required=False, allow_null=True)
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        not_fields = kwargs.pop('not_fields', None)
        image = kwargs.pop('image', False)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        if not_fields is not None:
            for field_name in not_fields:
                self.fields.pop(field_name)
        if image:
            self.fields.pop("image")
            self.fields["image"] = serializers.ListField(source="list_img")
    class Meta:
        model = PtqHistory
        fields = [
           "id","image","content","ptqId","times","createdAt","updatedAt","deletedAt","feedback","status","recordedName"
        ]
        
class PtqTypeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)
    createdAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="created_at", required=False, allow_null=True)
    updatedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="updated_at", required=False, allow_null=True)
    deletedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="deleted_at", required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        not_fields = kwargs.pop('not_fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        if not_fields is not None:
            for field_name in not_fields:
                self.fields.pop(field_name)
    
    class Meta:
        model = PtqType
        fields = [
           "id","type","createdAt","updatedAt","deletedAt","description"
        ]