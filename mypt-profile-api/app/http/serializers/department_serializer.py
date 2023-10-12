from rest_framework.serializers import *
from ..models.department import *


class DepartmentSerializer(ModelSerializer):
    childDepart = CharField(source='child_depart')
    codeChildDepart = CharField(source='code_child_depart')
    parentDepart = CharField(source='parent_depart')
    agency = CharField(source="chi_nhanh")

    def __init__(self, *args, **kwargs):

        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = Department
        fields = ['childDepart', 'parentDepart', 'codeChildDepart', 'branch', 'agency']


class DepartmentsSerializer(ModelSerializer):
    childDepart = CharField(source='child_depart')
    parentDepart = CharField(source='parent_depart')
    agency = CharField(source="chi_nhanh")

    def __init__(self, *args, **kwargs):

        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = Department
        fields = ['childDepart', 'parentDepart', 'branch', 'agency']
