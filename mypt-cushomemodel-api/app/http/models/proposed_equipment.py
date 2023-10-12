from django.db import models


# Create your models here.
class ProposedEquipment(models.Model):
    """
    modem_rule:
    1 - modem
    2 - access point
    """
    # device_origin:
    DEVICE_ORIGIN_MYPT = 'mypt'
    DEVICE_ORIGIN_MOBINET = 'mobinet'
    DEVICE_ORIGIN_MOBIQC = 'mobiqc'
    LIST_DEVICE_ORIGIN = {
        DEVICE_ORIGIN_MOBINET: 'Mobinet',
        DEVICE_ORIGIN_MOBIQC: 'MobiQC',
        DEVICE_ORIGIN_MYPT: 'My PT'
    }
    DEVICE_ORIGIN_CHOICES = (
        (DEVICE_ORIGIN_MOBINET, LIST_DEVICE_ORIGIN[DEVICE_ORIGIN_MOBINET]),
        (DEVICE_ORIGIN_MOBIQC, LIST_DEVICE_ORIGIN[DEVICE_ORIGIN_MOBIQC]),
        (DEVICE_ORIGIN_MYPT, LIST_DEVICE_ORIGIN[DEVICE_ORIGIN_MYPT]),
    )

    # modem_rule:
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

    # is_active:
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
        db_table = 'mypt_chm_proposed_equipment'

    id = models.BigAutoField(primary_key=True, auto_created=True)
    parent_name = models.CharField(max_length=100, null=False, blank=False)
    modem_rule = models.CharField(choices=MODEM_RULE_CHOICES, max_length=50, null=False, blank=False)
    lan_wifi = models.IntegerField(null=False)
    wifi = models.IntegerField(null=False)
    quantity_wan = models.IntegerField(null=False, default=0)
    wifi_24_ghz = models.IntegerField(null=True, default=None)
    wifi_5_ghz = models.IntegerField(null=True, default=None)
    device_origin = models.CharField(choices=DEVICE_ORIGIN_CHOICES, max_length=50, null=False, blank=False)
    created_at = models.DateTimeField(null=False, blank=False)
    updated_at = models.DateTimeField(null=True, blank=False)
    is_active = models.IntegerField(null=False, default=1)
    sdk_user_id = models.BigIntegerField(null=True, default=None)
    sdk_acc_username = models.CharField(max_length=255, null=True, default=None)

    def __str__(self):
        return self.parent_name
