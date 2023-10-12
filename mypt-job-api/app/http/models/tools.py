from django.db import models
from datetime import datetime, date
from ...configs.variable_system import EXPIRE_TOOL_STATUS, STATUS_TOOLS

class Tools(models.Model):
    id = models.BigAutoField(primary_key=True)
    scm_id = models.CharField(max_length=255, blank=True, null=True)
    item_code = models.CharField(max_length=255, blank=True, null=True)
    item_name = models.TextField(blank=True, null=True)
    size_name = models.CharField(max_length=255, blank=True, null=True)
    asset_code = models.CharField(max_length=255, blank=True, null=True)
    stock_name = models.CharField(max_length=255, blank=True, null=True)
    zone_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    serial = models.CharField(max_length=255, blank=True, null=True)
    quantity_now = models.IntegerField(blank=True, null=True)
    quantity_hold = models.IntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    expire_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    
    def status_tools(self, data):
        if data is None:
            return "NO_EXPIRED"
        delta = data - datetime.now().date()
        if delta.days < 0:
            return "EXPIRED"
        if delta.days <= EXPIRE_TOOL_STATUS:
            return "ABOUT_TO_EXPIRED"
        return "NO_EXPIRED"
    
    def status(self) -> str:
        return getattr(STATUS_TOOLS, self.status_tools(data=self.expire_date)).value
    
    def key_status(self) -> str:
        return str(self.status_tools(data=self.expire_date))
    
    class Meta:
        db_table = 'mypt_job_tools'
        