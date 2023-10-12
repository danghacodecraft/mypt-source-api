from rest_framework import serializers
from ....app.http.models.user_profile import UserProfile
from ...core.helpers import helper


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user_id', 'email', 'full_name', 'avatar_img']


class MyInfoUserProfileSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField(source="user_id")
    name = serializers.CharField(source='full_name')
    avatarImg = serializers.CharField(source='avatar_img')
    email = serializers.CharField()
    birthday = serializers.DateField(format="%d/%m/%Y")

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        data = super(MyInfoUserProfileSerializer, self).to_representation(instance)
        for key, value in data.items():
            if value is None or value == '':
                data[key] = '---'

        return data

    class Meta:
        model = UserProfile
        fields = ['userId', 'email', 'name', 'avatarImg', 'birthday']

    def get_avatar_from_email(email):
        avarta = ""
        try:
            qr = UserProfile.objects.filter(email=email).values_list('avatar_img', flat=True)
            avarta = qr[0]
        except Exception as ex:
            print("get_avatar_from_email >> Error/Loi: {}".format(ex))
        return avarta

    def get_avarta_from_user_id(user_id):
        avarta = ""
        try:
            qr = UserProfile.objects.filter(user_id=user_id).values_list('avatar_img', flat=True)
            avarta = qr[0]
        except Exception as ex:
            print("get_avatar_from_email >> Error/Loi: {}".format(ex))
        return avarta

