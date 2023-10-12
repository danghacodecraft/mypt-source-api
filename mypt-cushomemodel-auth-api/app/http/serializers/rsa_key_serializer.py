from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from app.http.models.rsa_key import RSAKey


class RSAKeySerializer(ModelSerializer):
    appId = serializers.CharField(source='app_id')
    publicKey = serializers.CharField(source='public_key')
    privateKey = serializers.CharField(source='private_key')
    dateCreated = serializers.DateTimeField(source='date_created', format='%Y-%m-%d %H:%M:%S')
    dateLastUpdated = serializers.DateTimeField(source='date_last_updated')

    class Meta:
        model = RSAKey
        fields = ['id', 'appId', 'publicKey', 'privateKey', 'dateCreated', 'dateLastUpdated']
