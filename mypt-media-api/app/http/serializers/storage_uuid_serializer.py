from rest_framework import serializers
from ..models.storage_uuid import *

class StorageUuidSerializer(serializers.ModelSerializer):
    # uuid = serializers.CharField(source='uuid')
    linkData = serializers.CharField(source='link_data')
    # email = serializers.CharField(source='email')
    updateTime = serializers.DateTimeField(source='update_time')
    linkLocal = serializers.CharField(source='link_local')
    # folder = serializers.CharField(source='folder')
    childFolder = serializers.CharField(source='child_folder')


    class Meta:
        model = StorageUuid
        fields = ['uuid', 'linkData', 'email', 'updateTime', 'linkLocal', 'folder', 'childFolder']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        foreignKey = kwargs.pop('foreignKey', None)

        super().__init__(*args, **kwargs)

        # if history_contact:
        #     self.fields['history_contact'] = HistoryContactSerializer(many=True)


        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if foreignKey is not None:
            self.fields.pop(foreignKey)

    # class EventSerializer(serializers.ModelSerializer):
    #     # Necessary information for API
    #     eventID = serializers.IntegerField(source='event_id')
    #     mobileImage = serializers.CharField(source='mobile_image')
    #     mobileButtonImage = serializers.CharField(source='mobile_button_image')
    #     actionType = serializers.CharField(source='action_type')
    #     dataAction = serializers.CharField(source='data_action')
    #     extraData = serializers.CharField(source='extra_data')
    #     popupType = serializers.CharField(source='popup_type')
    #     eventType = serializers.CharField(source='event_type')
    #     bannerLocation = serializers.CharField(source='banner_location')
    #
    #     class Meta:
    #         model = Events
    #         fields = ['eventID', 'title', 'eventType', 'description', 'mobileImage', 'mobileButtonImage', 'actionType',
    #                   'dataAction',
    #                   'extraData', 'popupType', 'bannerLocation']