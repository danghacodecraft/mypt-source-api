from django.db import models


# Create your models here.
class Equipments(models.Model):
    """
    modem_rule:
    1 - modem
    2 - access point
    """
    DEVICE_ORIGIN_INSIDE = 'inside'
    DEVICE_ORIGIN_TOOL_MANAGER = 'tool_quan_tri'
    DEVICE_ORIGIN_MYPT = 'mypt'
    DEVICE_ORIGIN_MOBINET = 'mobinet'
    DEVICE_ORIGIN_MOBIQC = 'mobiqc'
    LIST_DEVICE_ORIGIN = {
        DEVICE_ORIGIN_INSIDE: 'INSIDE',
        DEVICE_ORIGIN_TOOL_MANAGER: 'Tool quản trị',
        DEVICE_ORIGIN_MOBINET: 'Mobinet',
        DEVICE_ORIGIN_MOBIQC: 'MobiQC',
        DEVICE_ORIGIN_MYPT: 'My PT'
    }
    DEVICE_ORIGIN_CHOICES = (
        (DEVICE_ORIGIN_INSIDE, LIST_DEVICE_ORIGIN[DEVICE_ORIGIN_INSIDE]),
        (DEVICE_ORIGIN_TOOL_MANAGER, LIST_DEVICE_ORIGIN[DEVICE_ORIGIN_TOOL_MANAGER]),
        (DEVICE_ORIGIN_MOBINET, LIST_DEVICE_ORIGIN[DEVICE_ORIGIN_MOBINET]),
        (DEVICE_ORIGIN_MOBIQC, LIST_DEVICE_ORIGIN[DEVICE_ORIGIN_MOBIQC]),
        (DEVICE_ORIGIN_MYPT, LIST_DEVICE_ORIGIN[DEVICE_ORIGIN_MYPT]),
    )

    MODEM_RULE_TYPE_MODEM = 'modem'
    MODEM_RULE_TYPE_ACCESS_POINT = 'access_point'
    MODEM_RULE_TYPE_BOTH = 'both'
    LIST_MODEM_RULE_TYPES = {
        MODEM_RULE_TYPE_MODEM: 'Modem',
        MODEM_RULE_TYPE_ACCESS_POINT: 'Access Point',
        MODEM_RULE_TYPE_BOTH: 'Modem và Access Point'
    }
    MODEM_RULE_CHOICES = (
        (MODEM_RULE_TYPE_MODEM, LIST_MODEM_RULE_TYPES[MODEM_RULE_TYPE_MODEM]),
        (MODEM_RULE_TYPE_ACCESS_POINT, LIST_MODEM_RULE_TYPES[MODEM_RULE_TYPE_ACCESS_POINT]),
        (MODEM_RULE_TYPE_BOTH, LIST_MODEM_RULE_TYPES[MODEM_RULE_TYPE_BOTH])
    )

    IS_ACTIVE = 1
    NO_ACTIVE = 0
    LIST_STATUS_ACTIVE = {
        IS_ACTIVE: 'Có hiệu lực',
        NO_ACTIVE: 'Không hiệu lực'
    }
    STATUS_ACTIVE_CHOICES = (
        (IS_ACTIVE, LIST_STATUS_ACTIVE[IS_ACTIVE]),
        (NO_ACTIVE, LIST_STATUS_ACTIVE[NO_ACTIVE]),
    )

    class Meta:
        db_table = 'mypt_chm_equipments'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    parent_name = models.CharField(max_length=100, null=False, blank=False)
    code_id = models.IntegerField(null=True, blank=False)
    modem_rule = models.CharField(choices=MODEM_RULE_CHOICES, max_length=50, null=False, blank=False)
    lan_wifi = models.IntegerField(null=False, blank=False)
    wifi = models.IntegerField(null=False, blank=False)
    quantity_wan = models.IntegerField(null=False, blank=False)
    wifi_24_ghz = models.IntegerField(null=True, blank=False)
    wifi_5_ghz = models.IntegerField(null=True, blank=False)
    device_origin = models.CharField(choices=DEVICE_ORIGIN_CHOICES, max_length=50, null=True, blank=False)
    created_at = models.DateTimeField(null=False, blank=False)
    updated_at = models.DateTimeField(null=True, blank=False)
    is_active = models.IntegerField(choices=STATUS_ACTIVE_CHOICES, null=True, blank=False)
    mypt_user_id = models.BigIntegerField(null=True, blank=True)
    mypt_user_email = models.CharField(max_length=255, null=True, blank=True)
    mypt_user_fullname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.parent_name
