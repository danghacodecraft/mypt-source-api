from rest_framework import serializers
from ..models.setting_function_icons_model import *

class SettingFunctionIconsSerializer(serializers.ModelSerializer):
    iconId = serializers.IntegerField(source='icon_id', write_only=True, required=False)
    title = serializers.CharField(source='icon_title')
    permissionCodes = serializers.CharField(source='permission_codes')
    setIcon = serializers.DictField(source='icon_url')
    actionType = serializers.CharField(source='action_type')
    dataAction = serializers.CharField(source='data_action')
    extraData = serializers.CharField(source='extra_data')
    isDeleted = serializers.IntegerField(source='is_deleted', write_only=True)
    featureStatus = serializers.CharField(source='function_status')
    dateCreated = serializers.DateTimeField(source='date_created', write_only=True)
    dateModified = serializers.DateTimeField(source='date_modified', write_only=True)
    themeId = serializers.IntegerField(source="theme_id", required=False, allow_null=True, default=None)
    onHome = serializers.BooleanField(source="on_home", required=False, default=False)
    groupType = serializers.SerializerMethodField(source="group_type", required=False, default="")
    
    def get_groupType(self, value):
        if value.group_type is None:
            return ""
        return value.group_type

    def validate_title(self, title):
        if not self.instance:
            if SettingFunctionIcons.objects.filter(icon_title=title).exists():
                raise serializers.ValidationError("Function icon already exist")
        return title

    def update(self, instance, validated_data):
        try:
            instance.ordering = validated_data.get('ordering', instance.ordering)
            instance.permission_code = validated_data.get('permission_codes', instance.permission_codes)
            instance.icon_url = validated_data.get('icon_url', instance.icon_url)
            instance.action_type = validated_data.get('action_type', instance.action_type)
            instance.data_action = validated_data.get('data_action', instance.data_action)
            instance.extra_data = validated_data.get('extra_data', instance.extra_data)
            instance.is_deleted = validated_data.get('is_deleted', instance.is_deleted)
            instance.function_status = validated_data.get('function_status', instance.function_status)
            instance.date_created = validated_data.get('date_created', instance.date_created)
            instance.date_modified = validated_data.get('date_modified', instance.date_modified)
            instance.theme_id = validated_data.get('theme_id', instance.theme_id)
            instance.on_home = validated_data.get('on_home', instance.on_home)
            instance.group_type = validated_data.get('group_type', instance.group_type)
            instance.save()
        except Exception as ex:
            print("Error update function icon:", ex)
            raise serializers.ValidationError("Update function icon fail")
        return instance

    class Meta:
        model = SettingFunctionIcons
        fields = [
            'title',
            'ordering',
            'setIcon',
            'actionType',
            'dataAction',
            'extraData',
            'featureStatus',
            "iconId",
            "isDeleted",
            "dateCreated",
            "isDeleted",
            "dateModified",
            "permissionCodes",
            "themeId",
            "onHome",
            'groupType'
        ]