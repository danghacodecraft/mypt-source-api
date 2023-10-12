import json

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from app.core.helpers import global_variable as gb
from ..models.templates import Templates


class TemplatesSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False)
    groupID = serializers.IntegerField(required=True, allow_null=False, source='group_id', error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(
            item='ID nhóm'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(
            item='ID nhóm'),
        'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(
            item='ID nhóm'),
    })
    sketches = serializers.CharField(required=True, allow_blank=False, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(
            item='nét vẽ'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(
            item='nét vẽ'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(
            item='nét vẽ'),
    })
    sketchesType = serializers.CharField(required=False, allow_blank=False, allow_null=False, source='sketches_type',
                                         error_messages={
                                             'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(
                                                 item='loại nét vẽ'),
                                             'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(
                                                 item='loại nét vẽ'),
                                             'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(
                                                 item='loại nét vẽ'),
                                         })
    imageURL = serializers.CharField(required=True, allow_null=False, allow_blank=False, source='image_url',
                                     error_messages={
                                         'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(
                                             item='đường dẫn hình ảnh'),
                                         'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(
                                             item='đường dẫn hình ảnh'),
                                         'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(
                                             item='đường dẫn hình ảnh'),
                                     })
    createdAt = serializers.DateTimeField(required=False, source='created_at', format='%Y-%m-%d %H:%M:%S')
    updatedAt = serializers.DateTimeField(required=False, source='updated_at', format='%Y-%m-%d %H:%M:%S')
    myptUserId = serializers.IntegerField(required=True, allow_null=False, source='mypt_user_id',
                                          error_messages={
                                              'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(
                                                  item='userID My PT'),
                                              'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(
                                                  item='userID My PT'),
                                              'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(
                                                  item='userID My PT'),
                                          })
    myptUserEmail = serializers.CharField(required=True, allow_null=False, allow_blank=False, source='mypt_user_email',
                                          error_messages={
                                              'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(
                                                  item='email user My PT'),
                                              'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(
                                                  item='email user My PT'),
                                              'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(
                                                  item='email user My PT'),
                                          })
    myptUserFullName = serializers.CharField(required=True, allow_null=False, allow_blank=False,
                                             source='mypt_user_fullname',
                                             error_messages={
                                                 'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(
                                                     item='họ tên user My PT'),
                                                 'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(
                                                     item='họ tên user My PT'),
                                                 'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(
                                                     item='họ tên user My PT'),
                                             })

    class Meta:
        model = Templates
        fields = ['id', 'groupID', 'sketches', 'sketchesType', 'imageURL', 'createdAt', 'updatedAt', 'myptUserId',
                  'myptUserEmail', 'myptUserFullName']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            representation['sketches'] = json.loads(representation['sketches'])
        except Exception as ex:
            print('Error/Loi convert TemplatesSerializer' + str(ex))
        return representation
