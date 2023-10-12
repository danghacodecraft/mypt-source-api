from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from app.core.helpers import global_variable as gb
from app.core.helpers.my_datetime import getFormatDatetimeNow
from app.http.models.template_groups import TemplateGroups


class TemplateGroupsSerializer(ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=True, allow_blank=False, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(
            item='tên nhóm'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(
            item='tên nhóm'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(
            item='tên nhóm'),
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
        model = TemplateGroups
        fields = ['id', 'name', 'createdAt', 'updatedAt', 'myptUserId', 'myptUserEmail', 'myptUserFullName']

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
        return representation

    def create(self, validated_data):
        validated_data['created_at'] = getFormatDatetimeNow()
        template_group = TemplateGroups.objects.create(**validated_data)
        return validated_data
