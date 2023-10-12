from app.myHttp.models.user_infos import UserInfos
from rest_framework.serializers import ModelSerializer

class UserInfosSerializer(ModelSerializer):
    class Meta:
        model = UserInfos
        # fields = ['id', 'user_id', 'device_id', 'device_name', 'device_token']
        fields = '__all__'
        # extra_kwargs = {
        #     "id": {"required": True},
        #     "user_id": {"required": True}
        # }
