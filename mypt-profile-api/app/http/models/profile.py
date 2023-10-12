from django.db import models

from .department import *

from ..serializers.department_serializer import DepartmentSerializer


class Employee(models.Model):
    class Meta:
        db_table = 'employees_tb'

    email = models.CharField(max_length=50, primary_key=True)
    emp_code = models.CharField(max_length=8)
    emp_name = models.CharField(max_length=45)
    birthday = models.DateField()
    day = models.CharField(max_length=4)
    month = models.CharField(max_length=4)
    year = models.CharField(max_length=4)
    job_title = models.CharField(max_length=50)
    child_depart = models.CharField(max_length=30)
    mobile_phone = models.CharField(max_length=20)
    mstcn = models.CharField(max_length=50)
    dependent_info = models.CharField(max_length=50)
    contract_type = models.CharField(max_length=50)
    contract_code = models.CharField(max_length=30)
    contract_begin = models.DateField()
    contract_end = models.DateField()
    account_number = models.CharField(max_length=30)
    type_salary = models.CharField(max_length=50)
    sex = models.CharField(max_length=10)
    status_working = models.IntegerField()
    cmnd = models.CharField(max_length=30)
    date_join_company = models.DateField()
    date_quit_job = models.DateField()
    update_time = models.DateTimeField()
    update_by = models.CharField(max_length=45)
    avatar_img = models.CharField(max_length=200)
    id_user = models.CharField(max_length=50)

    ngay_cap_cmnd = models.DateField(blank=True, null=True)
    place_of_birth = models.CharField(max_length=200, blank=True, null=True)
    nationality = models.CharField(max_length=45, blank=True, null=True)
    noi_cap_cmnd = models.CharField(max_length=250, blank=True, null=True)
    place_of_permanent = models.CharField(max_length=255, blank=True, null=True)
    marital_status = models.IntegerField(blank=True, null=True)
    degree = models.CharField(max_length=45, blank=True, null=True)
    workplace = models.CharField(max_length=255, blank=True, null=True)
    level = models.CharField(max_length=45, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    health_insurance = models.CharField(max_length=30, blank=True, null=True)
    social_insurance = models.CharField(max_length=30, blank=True, null=True)
    social_insurance_salary_pay = models.CharField(max_length=100, blank=True, null=True)
    place_to_join_social_insurance = models.CharField(max_length=255, blank=True, null=True)
    tax_identification_place = models.CharField(max_length=255, blank=True, null=True)
    tax_identification_date = models.DateField(blank=True, null=True)

    foxpay = models.CharField(max_length=20, blank=True, null=True)

    salary_daily_date_last_sync = models.DateField(blank=True, null=True)
    salary_monthly_date_last_sync = models.DateField(blank=True, null=True)

    def locationJob(self):
        # if self.child_depart:
        #     try:
        #         queryset = Department.objects.filter(child_depart=self.child_depart)
        #         serializer = DepartmentSerializer(queryset, many=True, fields=["codeChildDepart"])
        #         code_location = serializer.data[0]
        #         queryset = Acronyms.objects.filter(code_ac=code_location)
        #         serializer = AcronymsSerializer(queryset, many=True, fields=["explainAc"])
        #         return serializer.data[0]
        #     except:
        #         return ""

        return ""

    def __str__(self):
        return self.email


class EmployeeRank(models.Model):
    class Meta:
        db_table = 'mypt_profile_employee_rank_pnc_tb'

    id = models.AutoField(primary_key=True)
    emp_code = models.CharField(max_length=20)
    emp_name = models.CharField(max_length=255)
    email = models.CharField(max_length=100)
    thang = models.IntegerField()
    nam = models.IntegerField()
    emp_rank_info = models.CharField(max_length=10000)
    bac_nghe = models.FloatField()
    update_time = models.DateTimeField()
    update_by = models.CharField(max_length=50)
    parent_depart = models.CharField(max_length=45)
    child_depart = models.CharField(max_length=45)