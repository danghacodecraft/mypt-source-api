from rest_framework import serializers
from ..models.list_folder import *

class ListFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListFolder
        fields = ['folder']