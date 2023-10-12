from rest_framework import serializers
from ..models.setting_users_home_tabs_model import *


class SettingUsersHomeTabsSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField(source='user_id')
    tabId = serializers.IntegerField(source='tab_id')
    shownStartDate = serializers.DateTimeField(source='shown_start_date')
    shownEndDate = serializers.DateTimeField(source='shown_end_date')
    isShown = serializers.IntegerField(source="is_shown")

    class Meta:
        model = SettingUserHomeTabs
        fields = ['userId', 'tabId', 'shownStartDate', 'shownEndDate', 'isShown']
