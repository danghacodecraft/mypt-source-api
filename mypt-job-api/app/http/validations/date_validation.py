from rest_framework.serializers import *
from datetime import datetime


class AddAccountVaidate(Serializer):
    code = CharField(required=True)
    deviceId = CharField(required=False)

    def validate_code(self, value):
        if len(value) != 8:
            raise ValidationError("Mã nhân viên phải đủ 8 số!")


class SalaryValidate(Serializer):
    monthStart = CharField()
    monthEnd = CharField()
    year = CharField()

    # def validate(self, data):

    #     if data['start'] > data['finish']:
    #         raise ValidationError("monthEnd must occur after monthStart")
    #     return data

    def validate_monthStart(self, value):
        if len(value) != 2:
            raise ValidationError("Tháng bắt đầu không đúng")
        if int(value) < 1 or int(value) > 12:
            raise ValidationError("Tháng sai định dạng")

    def validate_monthEnd(self, value):
        if len(value) != 2:
            raise ValidationError("Tháng bắt đầu không đúng")
        if int(value) < 1 or int(value) > 12:
            raise ValidationError("Tháng sai định dạng")

    def validate_year(self, value):
        if len(value) != 4:
            raise ValidationError("Năm không đúng")
