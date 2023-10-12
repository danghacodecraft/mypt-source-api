from django.db import models
from core.helpers.utils import *
from ...configs.service_api_config import *
import json
from django.db.models import Avg
from django.conf import settings as project_settings

class Ptq(models.Model):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.type_ptq = PtqType.objects.filter(type__isnull=False, deleted_at__isnull=True).values('id','description', 'type')
    class Meta:
        db_table = 'mypt_company_control'
    id = models.AutoField(primary_key=True) # 
    region = models.CharField(max_length=50)
    partner = models.CharField(max_length=50)
    block_name = models.CharField(max_length=50)
    emp_name = models.CharField(max_length=50)
    contract = models.CharField(max_length=50)
    error_type = models.CharField(max_length=50)
    date_complete = models.DateTimeField()
    error_main = models.CharField(max_length=50)
    error_group = models.CharField(max_length=50)
    error_description = models.CharField(max_length=50)
    error_detail = models.CharField(max_length=50)
    punishment = models.IntegerField()
    account_mbn = models.CharField(max_length=50)
    date_check = models.DateField()
    email = models.CharField(max_length=50)
    error_number = models.IntegerField()
    deadline = models.DateField()
    recorded = models.IntegerField(max_length=50)
    note = models.TextField()
    thematic = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    updated_by = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField()
    
    def get_type(self):
        try:
            if self.recorded:
                return self.type_ptq.get(id=self.recorded)["description"]
        except:
            return ""
        
    def get_key_type(self):
        try:
            if self.recorded:
                return self.type_ptq.get(id=self.recorded)["type"]
        except:
            return ""
    
class PtqHistory(models.Model):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.type_ptq = PtqType.objects.filter(type__isnull=False, deleted_at__isnull=True).values('id','description')
    class Meta:
        db_table = 'mypt_company_control_history'
    id = models.AutoField(primary_key=True) # 
    image = models.TextField()
    content = models.TextField()
    ptq_id = models.IntegerField()
    times = models.IntegerField()
    feedback = models.TextField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField()
    
    def get_type(self):
        try:
            if self.status:
                return self.type_ptq.get(id=self.status)["description"]
        except:
            return ""
    
    def list_img(self):
        if self.image:
            list_image = list(self.image.split(";"))
            try:
                list_image.remove("")
                return list_image
            except:
                return list_image
        return []
    
class PtqType(models.Model):
    class Meta:
        db_table = 'mypt_company_control_type'
    id = models.AutoField(primary_key=True) # 
    type = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField()