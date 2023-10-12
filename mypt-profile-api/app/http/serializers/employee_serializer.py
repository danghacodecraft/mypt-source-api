from rest_framework import serializers
from ..models.profile import *
from rest_framework.serializers import ModelSerializer

from ...core.helpers import helper
# from ...core.helpers import my_datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta as rd

# class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
#     code = serializers.CharField(source='emp_code')
#     name = serializers.CharField(source='emp_name')
#     id = serializers.CharField(source='id_user')

#     class Meta:
#         model = Employee

#         # It is strongly recommended that you explicitly set all fields that should be serialized using the fields attribute
#         # fields = ['emp_code', 'MBN_account_name', 'block_name', 'device_id', 'toa_do_van_phong', 'toa_do_kho', 'toa_do_lam_viec', 'ban_kinh_lam_viec', 'acctive_time']
#         fields = ['code', 'name', 'id', 'type_salary', 'email', 'birthday', 'day', 'month', 'year', 'job_title',
#                   'child_depart', 'mobile_phone', 'mstcn', 'dependent_info', 'contract_type', 'contract_begin',
#                   'contract_end', 'account_number', 'type_salary', 'sex', 'status_working', 'cmnd', 'date_join_company',
#                   'date_quit_job', 'update_time', 'update_by', 'avatar_img', 'id_user']
MARITAL_STATUS_TYPES = (
    (0, 'Chưa kết hôn'),
    (1, 'Đã kết hôn'),
    (2, 'Đã ly hôn')
)


class HomeEmployeeSerializer(serializers.HyperlinkedModelSerializer):
    empCode = serializers.CharField(source='emp_code')
    name = serializers.CharField(source='emp_name')
    avatarImg = serializers.CharField(source='avatar_img')
    class Meta:
        model = Employee

        # It is strongly recommended that you explicitly set all fields that should be serialized using the fields attribute
        # fields = ['emp_code', 'MBN_account_name', 'block_name', 'device_id', 'toa_do_van_phong', 'toa_do_kho', 'toa_do_lam_viec', 'ban_kinh_lam_viec', 'acctive_time']
        fields = ['empCode','name','avatarImg', 'sex']


class CodeEmployeeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Employee
        fields = ['emp_code']
        
class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    code = serializers.CharField(source='emp_code')
    name = serializers.CharField(source='emp_name')
    jobTitle = serializers.CharField(source='job_title')
    childDepart = serializers.CharField(source='child_depart')
    mobilePhone = serializers.CharField(source='mobile_phone')
    dependentInfo = serializers.CharField(source='dependent_info')
    contractType = serializers.CharField(source='contract_type')
    contractBegin = serializers.DateField(source='contract_begin', required=False, allow_null=True, format="%d/%m/%Y")
    contractEnd = serializers.DateField(source='contract_end', required=False, allow_null=True, format="%d/%m/%Y")
    accountNumber = serializers.CharField(source='account_number')
    typeSalary = serializers.CharField(source='type_salary')
    statusWorking = serializers.IntegerField(source='status_working')
    dateJoinCompany = serializers.DateField(source='date_join_company', required=False, allow_null=True, format="%d/%m/%Y")
    dateQuitJob = serializers.DateField(source='date_quit_job', required=False, allow_null=True, format="%d/%m/%Y")
    birthday = serializers.DateField(required=False, allow_null=True, format="%d/%m/%Y")
    updateTime = serializers.DateTimeField(source='update_time')
    updateBy = serializers.CharField(source='update_by')
    avatarImg = serializers.CharField(source='avatar_img')
    idUser = serializers.CharField(source='id_user')

    placeOfBirth = serializers.CharField(source='place_of_birth')
    maritalStatus = serializers.ChoiceField(source='marital_status',
                                            choices=MARITAL_STATUS_TYPES,
                                            default=0)

    def __init__(self, *args, **kwargs):
        
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = Employee
        fields = [
            'email', 'code', 'name',
            'birthday', 'day', 'month',
            'year', 'jobTitle', 'childDepart',
            'mobilePhone', 'mstcn', 'dependentInfo',
            'contractType', 'contractBegin', 'contractEnd',
            'accountNumber', 'typeSalary', 'sex',
            'statusWorking', 'cmnd', 'dateJoinCompany',
            'dateQuitJob', 'updateTime', 'updateBy',
            'avatarImg', 'idUser', "locationJob",

            "placeOfBirth", "nationality",  "maritalStatus"
        ]


class MyInfoEmployeeSerializer(serializers.ModelSerializer):
    userId = serializers.CharField(source='id_user')
    avatarImg = serializers.CharField(source='avatar_img')
    name = serializers.CharField(source='emp_name')
    code = serializers.CharField(source='emp_code')
    jobTitle = serializers.CharField(source='job_title')
    mobilePhone = serializers.CharField(source='mobile_phone')
    gender = serializers.CharField(source='sex')
    birthday = serializers.DateField(format="%d/%m/%Y")
    placeOfBirth = serializers.CharField(source='place_of_birth')
    childDepart = serializers.CharField(source='child_depart')
    identityCardNo = serializers.CharField(source='cmnd')
    date = serializers.DateField(format="%d/%m/%Y", source='ngay_cap_cmnd')
    issuedAt = serializers.CharField(source='noi_cap_cmnd')
    dateJoinCompany = serializers.DateField(format="%d/%m/%Y", source='date_join_company')
    dateQuitJob = serializers.DateField(format="%d/%m/%Y", source='date_quit_job')
    placeOfPermanent = serializers.CharField(source='place_of_permanent')
    maritalStatus = serializers.ChoiceField(source='marital_status',
                                            choices=MARITAL_STATUS_TYPES,
                                            default=0)
    accountNumber = serializers.CharField(source='account_number')
    bankName = serializers.CharField(source='bank_name')
    healthInsurance = serializers.CharField(source='health_insurance')
    socialInsurance = serializers.CharField(source='social_insurance')
    socialInsuranceSalaryPay = serializers.CharField(source='social_insurance_salary_pay')
    placeToJoinSocialInsurance = serializers.CharField(source='place_to_join_social_insurance')
    taxIdentificationNumber = serializers.CharField(source='mstcn')
    taxIdentificationPlace = serializers.CharField(source='tax_identification_place')
    taxIdentificationDate = serializers.DateField(format="%d/%m/%Y", source='tax_identification_date')
    contractType = serializers.CharField(source='contract_type')
    contractCode = serializers.CharField(source='contract_code')
    contractStartDate = serializers.DateField(format="%d/%m/%Y", source='contract_begin')
    contractEndDate = serializers.DateField(format="%d/%m/%Y", source='contract_end')
    recodedType = serializers.SerializerMethodField()
    totalDay = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        data = super(MyInfoEmployeeSerializer, self).to_representation(instance)
        for key, value in data.items():
            if value is None or value == '':
                data[key] = '---'
            if key == "maritalStatus":
                data[key] = str(data[key])
        return data

    def get_totalDay(self, employee):
        date_join_company = employee.date_join_company
        if date_join_company is not None and date_join_company:
            work_time_data = datetime.strptime(str(date_join_company), helper.format_date)
            time_now = datetime.strptime(str(datetime.now().date()), helper.format_date)
            working_day = (time_now - work_time_data).days + 1

            return f'{working_day}'
        return date_join_company

    def get_recodedType(self, contract):
        contract_end = contract.contract_end
        if contract_end and contract_end != "":
            contract_end = datetime.strptime(str(contract_end), helper.format_date)
            now_date = datetime.strptime(str(datetime.now().date()),
                                         helper.format_date)
            if contract_end < now_date:
                return "EXPIRED"
            return "DUE"
        return ""

    class Meta:
        model = Employee
        fields = ['userId', 'avatarImg', 'name', 'email', 'code',
                  'jobTitle', 'mobilePhone', 'gender', 'birthday',
                  'placeOfBirth', 'nationality', 'childDepart',
                  'identityCardNo', 'date', 'issuedAt',
                  'dateJoinCompany', 'dateQuitJob', 'placeOfPermanent',
                  'maritalStatus', 'degree', 'workplace',
                  'level', 'accountNumber', 'bankName',
                  'healthInsurance', 'socialInsurance', 'socialInsuranceSalaryPay',
                  'placeToJoinSocialInsurance',
                  'taxIdentificationNumber', 'taxIdentificationPlace', 'taxIdentificationDate',
                  'contractType', 'contractCode', 'contractStartDate', 'contractEndDate',
                  'recodedType',
                  'totalDay']


class EmployeeBirthdaySerializer(serializers.Serializer):
    class Meta:
        model = Employee
        fields = ["avatar", "fullname", "child_depart", "birthday", "sex", "email"]
    
    avatar = serializers.CharField(source='avatar_img')
    fullname = serializers.CharField(source='emp_name')
    child_depart = serializers.CharField()
    birthday = serializers.DateField()
    sex = serializers.CharField()
    email = serializers.SerializerMethodField()
    
    def get_email(self, employee):
        return employee.email.lower()
        
    
class EmployeeRankSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(required=False)
    emp_code = serializers.CharField(required=False)
    thang = serializers.IntegerField(required=False)
    nam = serializers.IntegerField(required=False)
    thang_nam = serializers.CharField(required=False)
    dung_hen = serializers.FloatField(required=False)
    cl7n = serializers.FloatField(required=False)
    nang_suat_co_he_so = serializers.FloatField(required=False)
    csat = serializers.FloatField(required=False)
    tong_so_mon = serializers.FloatField(required=False)
    tong_diem_cac_mon = serializers.FloatField(required=False)
    chuyen_mon = serializers.FloatField(required=False)
    tong_kien_thuc = serializers.FloatField(required=False)
    tong_diem_kien_thuc = serializers.FloatField(required=False)
    kien_thuc_khac = serializers.FloatField(required=False)
    chuong_trinh_thi_dua = serializers.FloatField(required=False)
    khen_thuong = serializers.FloatField(required=False)
    ky_luat = serializers.FloatField(required=False)
    cl7n_va_nsld = serializers.FloatField(required=False)
    diem_dung_hen = serializers.FloatField(required=False)
    diem_cl7n = serializers.FloatField(required=False)
    diem_nang_suat = serializers.FloatField(required=False)
    diem_csat = serializers.FloatField(required=False)
    diem_chuyen_mon = serializers.FloatField(required=False)
    diem_kien_thuc_khac = serializers.FloatField(required=False)
    diem_thi_dua = serializers.FloatField(required=False)
    diem_khen_thuong = serializers.FloatField(required=False)
    diem_ky_luat = serializers.FloatField(required=False)
    diem_cl7n_va_nsld = serializers.FloatField(required=False)
    tong_diem = serializers.FloatField(required=False)
    rank = serializers.IntegerField(required=False)
    update_time =  serializers.DateTimeField(required=False)
    update_by = serializers.CharField(required=False)
    parent_depart = serializers.CharField(required=False)
    child_depart = serializers.CharField(required=False)

    def __init__(self, *args, **kwargs):
        
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = EmployeeRank
        fields = [
            "id","emp_code","thang","nam","thang_nam","dung_hen",
            "cl7n","nang_suat_co_he_so","csat","tong_so_mon",
            "tong_diem_cac_mon","chuyen_mon","tong_kien_thuc",
            "tong_diem_kien_thuc","kien_thuc_khac","chuong_trinh_thi_dua",
            "khen_thuong","ky_luat","cl7n_va_nsld","diem_dung_hen",
            "diem_cl7n","diem_nang_suat","diem_csat","diem_chuyen_mon",
            "diem_kien_thuc_khac","diem_thi_dua","diem_khen_thuong",
            "diem_ky_luat","diem_cl7n_va_nsld","tong_diem","rank",
            "update_time","update_by","parent_depart","child_depart"
        ]