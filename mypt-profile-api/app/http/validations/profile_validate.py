from rest_framework import serializers
from rest_framework.serializers import *


class ListEmpCodeValidate(serializers.Serializer):
    empCode = serializers.ListField()


class ListEmailByUnitValidate(Serializer):
    unit = CharField(required=True,
                     error_messages={'required': 'unit là bắt buộc!',
                                     'blank': 'unit không được rỗng!',
                                     'null': 'unit không là giá trị null!'})
    unit_name = CharField(required=True,
                          error_messages={'required': 'unit_name là bắt buộc!',
                                          'blank': 'unit_name không được rỗng!',
                                          'null': 'unit_name không là giá trị null!'})

    def validate_unit(self, unit):
        if unit not in ["branch", "parent_depart", "agency", "child_depart"]:
            raise ValidationError("unit phải một trong các giá trị sau: branch, parent_depart, agency, child_depart!")
        return unit

    def validate(self, data):
        unit = data.get("unit")
        unit_name = data.get("unit_name")
        if unit == "branch" and unit_name not in ["ALL", "TIN", "PNC", "TINPNC"]:
            raise ValidationError('unit là branch thì unit_name phải thuộc các giá trị: ALL, TIN, PNC, TINPNC')
        return data
