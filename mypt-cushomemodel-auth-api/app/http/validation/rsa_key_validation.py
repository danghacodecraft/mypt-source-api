from rest_framework import serializers

from app.core.entities.my_rsa_alogrithm import MyRSA
from app.http.models.rsa_key import RSAKey


class RSAKeyCreateValidate(serializers.Serializer):
    appId = serializers.CharField(required=False, error_messages={
        'required': 'appId là bắt buộc',
        'blank': 'appId không được để trống'
    }, source='app_id')
    dateCreated = serializers.DateTimeField(required=False, source='date_created', format='%Y-%m-%d %H:%M:%S')

    def create(self, validated_data):
        # Tạo rsa
        my_rsa = MyRSA()
        public_key, private_key = my_rsa.create_rsa_key()
        rsa_key = RSAKey.objects.create(
            app_id=validated_data['app_id'],
            public_key=public_key,
            private_key=private_key,
            date_created=None,
            date_last_updated=None
        )
        rsa_key.save()
        return rsa_key
