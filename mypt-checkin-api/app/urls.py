from django.urls import path


from .http.views.emp_checkin_view import *

from .http.views.update_info_checkin_view import *
from .http.views.healthcheck_view import *
from .http.views.list_data_view import *
from .http.views.add_info_checkin_view import *
from .http.views.cron_view import *

urlpatterns = [
    path('health', HealthCheckView.as_view({'get': 'health_check'})),

    path('provide-info-device', AddInfoCheckinView.as_view({'get': 'provide_info_device'})),
    path('send-response', AddInfoCheckinView.as_view({'post': 'send_response'})),

    path("get-coordinate", UpdateInfoCheckinView.as_view({'post': 'get_coordinate'})),
    path('confirm-info-checkin', UpdateInfoCheckinView.as_view({'post': 'confirm_info_checkin'})),

    path('get-info-emp-checkin', EmpCheckinView.as_view({'get':'get_emp_info_checkin'})),

    path('list-response', ListDataView.as_view({'get': 'list_response'})),
    path('report-checkin-on-month', EmpCheckinView.as_view({'get': 'report_checkin_on_month'})),
    path('cron', CronView.as_view({'get': 'cron'})),
    path('cron1', CronView.as_view({'get': 'cron_start'})),

    path('get_info_checkin_from_emp_code', EmpCheckinView.as_view({'get':'get_info_checkin_from_emp_code'}))

    # path("refresh-data-checkin", refresh_data_checkin.refresh_data_checkin),
    # path("refresh-data-device", refresh_data_device.refresh_data_device),




]
