from rest_framework.viewsets import ViewSet
from ...serializers.employee_serializer import *
from profile_app.core.helpers.response import response_data
from profile_app.core.helpers.utils import *

class CheckinView(ViewSet):
    def api_get_info_from_emp_code(self, request):
        fname = "api_get_info_from_emp_code"
        data_input = request.data
        emp_code = data_input.get("empCode", "")
        try:
            qr = Employee.objects.filter(emp_code=emp_code).values()
            if len(qr) == 0:
                return response_data(data={}, message="Không có data", status=5)

            info_emp = qr[0]

            date_join_company = convert_date_export( info_emp['date_join_company'])
            data_output = {
                "dateJoinCompany": date_join_company
            }
            return response_data(data=data_output, message="Thành công", status=1)
        except Exception as ex:
            print("{} >> {}: Error/loi: {}".format(datetime.now(), fname, ex))
