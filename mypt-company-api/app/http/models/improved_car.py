from django.db import models
from core.helpers.utils import *
from ...configs.service_api_config import *
import json
from django.db.models import Avg
from django.conf import settings as project_settings

class ImprovedCar(models.Model):
    class Meta:
        db_table = 'mypt_company_improve_car_tb'

    id = models.AutoField(primary_key=True)
    type_title = models.IntegerField() 
    email_create = models.CharField(max_length=45)
    name_xe_cai_tien = models.CharField(max_length=500)
    group_xe_cai_tien = models.IntegerField()
    member_group = models.CharField(max_length=1000)
    current_status = models.CharField(max_length=5000)
    purpose = models.CharField(max_length=5000)
    solution = models.CharField(max_length=5000)
    effective = models.CharField(max_length=1000)
    creative = models.CharField(max_length=1000)
    possibility = models.CharField(max_length=1000)
    note = models.CharField(max_length=1000)
    update_time = models.DateTimeField(auto_now=True)
    branch = models.CharField(max_length=45)
    img_xe_cai_tien = models.CharField(max_length=200)
    parent_depart = models.CharField(max_length=45)
    agency = models.CharField(max_length=45)
    process_status = models.CharField(max_length=45, default='unpublish')
    
    def sum_like(self):
        if self.id:
            id = self.id
            queryset = ImprovedCarLike.objects.filter(id_tree=id, state_like=1)
            return queryset.count()
        return 0
    
    def sum_rate(self):
        try:
            if self.id:
                id = self.id
                queryset = RateTheArticle.objects.filter(id_tree=id, deleted_at__isnull=True)
                avg = list(queryset.aggregate(Avg('rate')).values())[0]
                if not avg:
                    avg = 5.0
                return {
                    "sum": queryset.count(),
                    "avg": avg
                }
        except:
            return {
                "sum": 0,
                "avg": 5.0
            }
        
    def sum_comment(self):
        if self.id:
            id = self.id
            queryset = ImprovedCarComment.objects.filter(id_tree=id, deleted_at__isnull=True)
            return queryset.count()
        return 0
    def get_update_date(self):
        if self.update_time:
            datatime = self.update_time
            timeresult = str(datatime.strftime("%d-%m-%Y"))
            return timeresult
        return None
    def get_update_time(self):
        if self.update_time:
            datatime = self.update_time
            timeresult = str(datatime.strftime("%H:%M"))
            return timeresult
        return None    
    def list_img(self):
        if self.img_xe_cai_tien:
            list_image = list(self.img_xe_cai_tien.split(";"))
            try:
                list_image.remove("")
                return list_image
            except:
                return list_image
        return []
        

class ImprovedCarLike(models.Model):
    class Meta:
        db_table = 'mypt_company_improve_car_like_tb'
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=45)
    id_tree = models.IntegerField()
    state_like = models.IntegerField()


class ImprovedCarGroup(models.Model):
    class Meta:
        db_table = 'mypt_company_improve_car_group'
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField()
    

class ImprovedCarComment(models.Model):
    class Meta:
        db_table = 'mypt_company_improve_car_history_msg_tb'

    id = models.AutoField(primary_key=True)
    parent = models.IntegerField()
    email = models.CharField(max_length=45)
    msg = models.CharField(max_length=10000)
    id_tree = models.IntegerField()
    t_create = models.DateTimeField()
    type = models.IntegerField()
    level = models.IntegerField()
    deleted_at = models.DateField()


class RateTheArticle(models.Model):
    class Meta:
        db_table = 'mypt_company_improve_car_rate_the_article'

    id = models.AutoField(primary_key=True)
    content = models.TextField()
    effective = models.TextField()
    creative = models.TextField()
    possibility = models.TextField()
    email = models.CharField(max_length=255)
    rate = models.IntegerField(max_length=2)
    id_tree = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField()
