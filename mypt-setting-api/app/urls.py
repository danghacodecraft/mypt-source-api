from django.urls import path
from .http.views.health_view import *
from .http.views.setting_view import *
from .http.views.device_permission_logger_view import *
from .http.views.setting_config_view import SettingConfigViewSet
from .http.views.email_template_view import EmailTemplateViewSet
from .http.views.email_service_view import EmailReportViewSet
from .http.views.cron_view import CronViewSet

"""----- UN-ALLOWED DELETE THE LINE BELOW -----"""
from .core.helpers import execute_on_startup
"""--------------------------------------------"""

urlpatterns = [
    path('health', SettingHealthCheckView.as_view({'get': 'getHealthCheck'})),
    path('configs', SettingView.as_view({'post': 'postConfigs'})),
    path('get-all-functions', SettingView.as_view({'get': 'get_all_functions'})),
    path('add-function', SettingView.as_view({'post': 'add_function'})),
    path('update-function', SettingView.as_view({'post': 'update_function'})),
    path('remove-function', SettingView.as_view({'post': 'remove_function'})),
    path('test-get-user-session', SettingHealthCheckView.as_view({'post': 'testGetUserSession'})),
    path('assign-default-tabs-to-user', SettingView.as_view({'post': 'assignDefaultTabsToUser'})),
    path('update-shown-start-date-users-home-tabs', SettingView.as_view({'post': 'updateShownStartDateUsersHomeTabs'})),
    path('show-hide-user-home-tab', SettingView.as_view({'post': 'showHideUserHomeTab'})),
    path('remove-setting-config', SettingView.as_view({'post': 'remove_setting_config'})),
    path('get-setting-config', SettingView.as_view({'post': 'get_setting_config'})),

    path('add-new-device-permission', DevicePermissionsViewSet.as_view({'post': 'add_new_device_permission'})),
    path('get-device-permissions-info', DevicePermissionsViewSet.as_view({'get': 'get_device_permissions_info'})),
    path('remove-device-permission', DevicePermissionsViewSet.as_view({'post': 'remove_device_permission'})),
    path('add-log', DevicePermissionLoggerViewSet.as_view({'post': 'add_log'})),
    path('get-logs', DevicePermissionLoggerViewSet.as_view({'post': 'get_logs'})),
    path('clear-logs', DevicePermissionLoggerViewSet.as_view({'post': 'clear_logs'})),
    path('export-report', DevicePermissionLoggerViewSet.as_view({'post': 'export_report'})),
    path('add-or-update-last-change', DevicePermissionLoggerViewSet.as_view({'post': 'add_or_update_last_change'})),
    path('get-logs-last-change', DevicePermissionLastChangeView.as_view({'post': 'get_logs_last_change'})),
    
    path('set-config', SettingConfigViewSet.as_view({'post': 'set_config'})),
    path('get-config', SettingConfigViewSet.as_view({'post': 'get_config'})),
    path('remove-config', SettingConfigViewSet.as_view({'post': 'remove_config'})),
    
    path('add-template', EmailTemplateViewSet.as_view({'post': 'add_template'})),
    path('remove-template', EmailTemplateViewSet.as_view({'post': 'remove_template'})),
    
    path('send-report-email', EmailReportViewSet.as_view({'post': 'send_report_email'})),
    path('send-email', EmailReportViewSet.as_view({'post': 'send_one_mail'})),
    path('send-email-with-template', EmailReportViewSet.as_view({'post': 'send_with_template'})),
    path('capture-image-report', EmailReportViewSet.as_view({'post': 'capture_one_image'})),
    path('capture-image-report-review', EmailReportViewSet.as_view({'post': 'capture_image_report_review'})),
    path('clear-all-schedules', EmailReportViewSet.as_view({'get': 'clear_all_schedules'})), 
    path('clear-schedule', EmailReportViewSet.as_view({'post': 'clear_schedule'})),
    path('email-initial', EmailReportViewSet.as_view({'get': 'email_initial'})),
    
    path("add-new-task", CronViewSet.as_view({"post": "add_new_task"})),
    path("get-task-info", CronViewSet.as_view({"post": "get_task_info"})),
    path("remove-task", CronViewSet.as_view({"post": "remove_task"})),
    path("remove-all-tasks", CronViewSet.as_view({"post": "remove_all_tasks"})),
    path("refresh-cron-service", CronViewSet.as_view({"get": "refresh"})),
    path("cron-initial", CronViewSet.as_view({"get": "cron_initial"})),
    path("staging-call-to-production", CronViewSet.as_view({"post": "staging_call_to_production"})),
    
    path("say-hello", CronViewSet.as_view({"post": "say_hello"})),
    path("call-api", CronViewSet.as_view({"post": "call"})),
]

