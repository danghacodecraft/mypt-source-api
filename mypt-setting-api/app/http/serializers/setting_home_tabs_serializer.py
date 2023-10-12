from rest_framework import serializers
from ..models.setting_home_tabs_model import *


class SettingHomeTabsSerializer(serializers.ModelSerializer):
    tabId = serializers.IntegerField(source='tab_id')
    tabName = serializers.CharField(source='tab_name')
    tabCode = serializers.CharField(source='tab_code')
    appVersion = serializers.CharField(source='app_version')
    isDefault = serializers.IntegerField(source="is_default")

    class Meta:
        model = SettingHomeTabs
        fields = ['tabId', 'tabName', 'tabCode', 'appVersion', 'isDefault']