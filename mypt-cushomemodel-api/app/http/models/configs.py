from django.db import models


# Create your models here.
class Configs(models.Model):
    CONFIG_TYPE_CONSTANT = 'constant'
    CONFIG_TYPE_REMOTE = 'remote'
    CONFIG_TYPE_MESSAGE = 'message'
    LIST_CONFIG_TYPE = {
        CONFIG_TYPE_CONSTANT: 'constant',
        CONFIG_TYPE_REMOTE: 'remote',
        CONFIG_TYPE_MESSAGE: 'message'
    }
    CONFIG_TYPE_CHOICES = (
        (CONFIG_TYPE_CONSTANT, LIST_CONFIG_TYPE[CONFIG_TYPE_CONSTANT]),
        (CONFIG_TYPE_REMOTE, LIST_CONFIG_TYPE[CONFIG_TYPE_REMOTE]),
        (CONFIG_TYPE_MESSAGE, LIST_CONFIG_TYPE[CONFIG_TYPE_MESSAGE])
    )

    # status
    CONFIG_STATUS_DISABLED = 'disabled'
    CONFIG_STATUS_ENABLED = 'enabled'
    CONFIG_STATUS_DELETED = 'deleted'
    LIST_CONFIG_STATUS = {
        CONFIG_STATUS_DISABLED: 'disabled',
        CONFIG_STATUS_ENABLED: 'enabled',
        CONFIG_STATUS_DELETED: 'deleted'
    }
    CONFIG_STATUS_CHOICES = (
        (CONFIG_STATUS_DISABLED, LIST_CONFIG_STATUS[CONFIG_STATUS_DISABLED]),
        (CONFIG_STATUS_ENABLED, LIST_CONFIG_STATUS[CONFIG_STATUS_ENABLED]),
        (CONFIG_STATUS_DELETED, LIST_CONFIG_STATUS[CONFIG_STATUS_DELETED])
    )

    class Meta:
        db_table = 'mypt_chm_configs'

    config_id = models.BigAutoField(primary_key=True, auto_created=True)
    config_type = models.CharField(max_length=20, choices=CONFIG_TYPE_CHOICES, default=CONFIG_TYPE_MESSAGE, null=False, blank=False)
    config_key = models.CharField(max_length=100)
    config_value = models.TextField(null=False, blank=False)
    config_description_vi = models.TextField()
    config_description_en = models.TextField()
    config_status = models.CharField(max_length=20, choices=CONFIG_STATUS_CHOICES, default=CONFIG_STATUS_ENABLED, null=False, blank=False)
    owner = models.CharField(max_length=100, default='longthk', null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(null=True, blank=False)
    note = models.CharField(max_length=255)

    def __str__(self):
        return self.config_key
