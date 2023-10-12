from django.urls import path

from .http.views.health_view import HealthView
from .http.views.kpi_view import KpiView
from .http.views.salary_view import SalaryView
from .http.views.tracking_view import TrackingView
from .http.views.config_manager_view import ConfigManagerView
from .http.views.cache_manager_view import CacheManagerView
from .http.views.tool_view import ToolView

urlpatterns = [
    path('health', HealthView.as_view({'get': 'health'})),
    path('get-kpi-result', KpiView.as_view({'get': 'get_kpi_result'})),
    path('get-kpi-list-chart', KpiView.as_view({'get': 'get_kpi_list_chart'})),
    path('get-kpi-detail-info', KpiView.as_view({'get': 'get_kpi_detail_info'})),
    path('get-csat-list-chart', KpiView.as_view({'get': 'get_csat_list_chart'})),
    # SALARY
    path('get-salary-in-home', SalaryView.as_view({'get': 'get_salary_in_home'})),
    path('get-salary-provisional-overview', SalaryView.as_view({'get': 'get_salary_provisional_overview'})),
    path('get-salary-provisional-by-date', SalaryView.as_view({'post': 'get_salary_provisional_by_date'})),
    path('get-salary-formula-by-month', SalaryView.as_view({'post': 'get_salary_formula_by_month'})),
    path('get-salary-real-by-month', SalaryView.as_view({'post': 'get_salary_real_by_month'})),
    path('tracking-action', TrackingView.as_view({'post': 'tracking_action'})),
    
    path('get-all-cache', CacheManagerView.as_view({'get': 'get_all_cache'})),
    path('get-cache-value-by-key', CacheManagerView.as_view({'get': 'get_cache_value_by_key'})),
    path('clear-cache-by-key', CacheManagerView.as_view({'get': 'clear_cache_by_key'})),
    path('clear-cache-by-prefix', CacheManagerView.as_view({'get': 'clear_cache_by_prefix'})),
    
    path('get-all-configs', ConfigManagerView.as_view({'get': 'get_all_configs'})),
    
    path('get-config-value-by-key', ConfigManagerView.as_view({'get': 'get_config_value_by_key'})),
    path('update-config-value-by-key', ConfigManagerView.as_view({'get': 'update_config_by_key'})),
    path('sync-salary-inside-data-daily', SalaryView.as_view({'get': 'sync_salary_inside_data_daily'})),
    path('sync-salary-inside-data-monthly', SalaryView.as_view({'get': 'sync_salary_inside_data_monthly'})),
    path('remove-salary-monthly-and-update-last-sync-date', SalaryView.as_view(
        {'get': 'remove_salary_monthly_and_update_last_sync_date'})),
    path('remove-salary-daily-before-sync-date', SalaryView.as_view({'get': 'remove_salary_daily_before_sync_date'})),
    path('remove-duplicate-salary-daily', SalaryView.as_view({'post': 'remove_duplicate_salary_daily'})),
    path('remove-duplicate-salary-daily-total', SalaryView.as_view({'post': 'remove_duplicate_salary_daily_total'})),
    path('remove-duplicate-salary-monthly', SalaryView.as_view({'post': 'remove_duplicate_salary_monthly'})),
    path('show-tools', ToolView.as_view({'get': 'show_tools'})),
    path('count-tools-expiration', ToolView.as_view({'get': 'count_tools_expiration'})),
    path('call-scm', ToolView.as_view({'get': 'call_scm'})),
    path('add-tools', ToolView.as_view({'post': 'add_tools'})),
    path('view-cache', ToolView.as_view({'post': 'view_cache'})),
    path('test-create', ToolView.as_view({'post': 'test_create'})),
]
