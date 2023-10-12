from django.urls import path

from .http.views.birthday_view import BirthDayViewSet
from .http.views.checkin.checkin_view import *
from .http.views.cron import Cron
from .http.views.device_permission_logger_view import *
from .http.views.profile_view import *

urlpatterns = [
    path('employee', ProfileView.as_view({'get': 'get_employee_info'})),
    path('employee-new', ProfileView.as_view({'get': 'get_employee_info_new'})),
    path('get-profile-info', ProfileView.as_view({'post': 'check_get_employee'})),
    path('health', ProfileView.as_view({'get': 'health_check'})),
    path('get-all-profile', ProfileView.as_view({'get': 'get_all_profile'})),
    path('get-profile-overview', ProfileView.as_view({'get': 'get_profile_overview'})),
    path('get-profile-detail', ProfileView.as_view({'get': 'get_profile_detail'})),
    path('get-working-information', ProfileView.as_view({'get': 'get_working_information'})),
    path('get-salary-account', ProfileView.as_view({'get': 'get_salary_account'})),
    path('get-insurance-tax', ProfileView.as_view({'get': 'get_insurance_tax'})),
    path('get-contracts', ProfileView.as_view({'get': 'get_contracts'})),
    path('get-occupational-safety-cards', ProfileView.as_view({'get': 'occupational_safety_card_by_emp_code'})),
    path('get-application-info', ProfileView.as_view({'get': 'get_application_info'})),
    path('get-device-info', ProfileView.as_view({'get': 'get_device_info'})),
    path('update-avatar', ProfileView.as_view({'post': 'update_avatar'})),
    path('update-birthday-profile', ProfileView.as_view({'post': 'update_birthday_profile'})),
    path('info-child-depart-for-list-email', ProfileView.as_view({'post': 'api_info_child_depart_for_list_email'})),
    path('save-redis-region', ProfileView.as_view({'post': 'api_save_redis_region'})),

    path('info-to-email', ProfileView.as_view({'post': 'info_to_email'})),
    path('email-list-from-branch', ProfileView.as_view({'get': 'get_email_list_from_branch'})),
    path('get-list-email-by-unit', ProfileView.as_view({'post': 'get_list_email_by_unit'})),
    path('email-to-list-code', ProfileView.as_view({'post': 'email_to_list_code'})),
    # start: job goi de dong bo luong
    path('get-employee-from-email', ProfileView.as_view({'post': 'get_employee_from_email'})),
    path('get-all-employee-empty-salary-daily', ProfileView.as_view({'post': 'get_all_employee_empty_salary_daily'})),
    path('get-all-employee-empty-salary-monthly',
         ProfileView.as_view({'post': 'get_all_employee_empty_salary_monthly'})),
    path('update-employee-salary-day-sync-status',
         ProfileView.as_view({'post': 'update_employee_salary_day_sync_status'})),
    path('update-employee-salary-month-sync-status',
         ProfileView.as_view({'post': 'update_employee_salary_month_sync_status'})),
    # end: job goi de dong bo luong
    path('cron', Cron.as_view({'get': 'cron_start'})),
    # path('task-kpi', JsonView.as_view({'post': 'task_kpi'})),

    path('get-employees-whose-birthday-is-today-and-their-colleagues-info',
         BirthDayViewSet.as_view({'get': 'get_employees_whose_birthday_is_today_and_their_colleagues_info'})),

    path('add-new-device-permission', DevicePermissionsViewSet.as_view({'post': 'add_new_device_permission'})),
    path('get-device-permissions-info', DevicePermissionsViewSet.as_view({'get': 'get_device_permissions_info'})),
    path('remove-device-permission', DevicePermissionsViewSet.as_view({'post': 'remove_device_permission'})),
    path('add-log', DevicePermissionLoggerViewSet.as_view({'post': 'add_log'})),
    path('get-logs', DevicePermissionLoggerViewSet.as_view({'post': 'get_logs'})),
    path('clear-logs', DevicePermissionLoggerViewSet.as_view({'post': 'clear_logs'})),
    path('export-report', DevicePermissionLoggerViewSet.as_view({'post': 'export_report'})),
    path('add-or-update-last-change', DevicePermissionLoggerViewSet.as_view({'post': 'add_or_update_last_change'})),
    path('get-logs-last-change', DevicePermissionLastChangeView.as_view({'get': 'get_logs_last_change'})),

    # Lấy email PDX, features_roles_emails cho service company
    path('get-list-email-pdx', ProfileView.as_view({'get': 'get_list_email_pdx'})),
    path('get-features-roles-emails-improve-car', ProfileView.as_view(
        {'get': 'get_features_roles_emails_improve_car'})),

    # Lay ngay join company cho service checkin,
    path('get-info-emp-for-checkin', CheckinView.as_view({'post': 'api_get_info_from_emp_code'})),

    # Lay thong tin employee cho danh sach cac email
    path('emps-info-by-emails', ProfileView.as_view({'post': 'emps_info_by_emails'})),
    # lay avatar tu email, api goi noi bo
    path('get-list-avatar-from-list-email', ProfileView.as_view({'post': "get_list_avatar_from_list_email"}))
]
