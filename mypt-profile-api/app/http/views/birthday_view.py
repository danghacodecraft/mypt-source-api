from rest_framework.viewsets import ViewSet
# from ..models.profile import Employee

from ..serializers.employee_serializer import *
from ....app.core.helpers.response import response_data
from datetime import *

class BirthDayViewSet(ViewSet):
    def get_employees_whose_birthday_is_today_and_their_colleagues_info(self, request_data):
        try:
            today = datetime.now().date()
            queryset = Employee.objects.filter(
                status_working=1
            )
            
            queryset_emp_birthday_is_today = queryset.filter(
                birthday__day=today.day,
                birthday__month=today.month
            )
            serializer_emp_birthday_is_today = EmployeeBirthdaySerializer(queryset_emp_birthday_is_today, many=True).data
            res_data = []
            
            for serializer_emp in serializer_emp_birthday_is_today:
                queryset_colleagues = queryset.filter(child_depart=serializer_emp['child_depart'])
                serializer_colleagues = EmployeeBirthdaySerializer(queryset_colleagues, many=True).data
                dataset = {
                    "user": serializer_emp,
                    "colleagues": serializer_colleagues
                }
                res_data.append(dataset)
            return response_data(res_data)
        except Exception as e:
            print(f"{datetime.now()} >> get_employees_whose_birthday_is_today_and_their_colleagues_info >> {e}")
            return response_data(status=4, message=str(e))