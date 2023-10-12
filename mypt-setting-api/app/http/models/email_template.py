from django.db import models

class EmailTemplate(models.Model):
    class Meta:
        db_table = 'mypt_setting_email_template'
    
    id  = models.AutoField(primary_key=True)
    template_name = models.CharField(max_length=100, unique=True)
    field_require = models.TextField()
    html = models.TextField()
    is_deleted = models.BooleanField(default=False)
    