from rest_framework import serializers
from ..models.safe_card import *
from datetime import datetime
from ...core.helpers import helper, utils
from ...core.helpers.global_data import VIEW_FILE_AUTH_PUBLIC
from ...configs.variable import *
from ...configs.service_api_config import *
from ...configs.app_settings import AES_SECRET_KEY
from django.conf import settings as project_settings
from ...core.helpers import auth_session_handler as authSessionHandler
import pyshorteners


class SafeCardSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="atld_id", required=False)
    empCode = serializers.CharField(source="emp_code", required=False)
    trainningGroup = serializers.CharField(source="nhom_dao_tao", required=False)
    certificate = serializers.CharField(source="cap_the_chung_chi", required=False)
    dateCertificate = serializers.DateField(source="ngay_cap_the_ATLD", required=False)
    expirationDate = serializers.DateField(source="ngay_het_han_ATLD", required=False)
    trainingStartDate = serializers.DateField(source="ngay_bat_dau_dao_tao", required=False)
    trainingEndDate = serializers.DateField(source="ngay_ket_thuc_dao_tao", required=False)
    statusCertificate = serializers.CharField(source="tinh_trang_the_chung_chi", required=False)
    pictureCertificate = serializers.CharField(source="hinh_anh_the_chung_nhan", required=False)
    updateTime = serializers.DateTimeField(source="update_time_atld", required=False)
    updateBy = serializers.CharField(source="update_by", required=False)

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        # data = self.fields.pop("emp_info")
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SafeCard
        fields = [
            "id", "empCode", "trainningGroup", "certificate",
            "dateCertificate", "expirationDate", "trainingStartDate",
            "trainingEndDate", "statusCertificate", "pictureCertificate",
            "updateTime", "updateBy"
        ]


class MyInfoSafeCardSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source="nhom_dao_tao", required=False)
    occupationalSafetyCardNumber = serializers.CharField(source="so_the_ATLD", required=False)
    certificateDate = serializers.DateField(format="%d/%m/%Y", source="ngay_cap_the_ATLD", required=False)
    expirationDate = serializers.DateField(format="%d/%m/%Y", source="ngay_het_han_ATLD", required=False)
    certificate = serializers.CharField(source="cap_the_chung_chi", required=False)
    certificatePicture = serializers.SerializerMethodField()
    recodedName = serializers.SerializerMethodField()
    recodedType = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        data = super(MyInfoSafeCardSerializer, self).to_representation(instance)

        for key, value in data.items():
            if value is None or value == "":
                data[key] = "---"

        return data

    def get_certificatePicture(self, safe_card_obj):
        request = self.context.get('request', None)

        if request is None:
            return ""

        certificate_picture = safe_card_obj.hinh_anh_the_chung_nhan
        uuid_split = certificate_picture.split("?path=")
        user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        if len(uuid_split) == 2:
            path = utils.encrypt_aes(AES_SECRET_KEY, uuid_split[1] + ";" + str(user_token["userId"]))
            full_url = VIEW_FILE_AUTH_PUBLIC + path
            return full_url
        return ""

    def get_recodedName(self, safe_card_obj):
        certificate_status = safe_card_obj.tinh_trang_the_chung_chi
        if certificate_status and certificate_status != "":
            return certificate_status
        return "---"

    def get_recodedType(self, safe_card_obj):
        certificate_status = safe_card_obj.tinh_trang_the_chung_chi
        if certificate_status and certificate_status != "":
            if certificate_status == "Chưa Cấp":
                return "NO"
            elif certificate_status == "Còn Hạn":
                return "DUE"
            elif certificate_status == "Hết Hạn":
                return "EXPIRED"
            else:
                return "EXPIRING_SOON"
        return "---"

    class Meta:
        model = SafeCard
        fields = [
            "occupationalSafetyCardNumber",
            "group",
            "certificateDate",
            "expirationDate",
            "certificate",
            "certificatePicture",
            "recodedName",
            "recodedType",
        ]
