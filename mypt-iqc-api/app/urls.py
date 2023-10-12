from django.urls import path

from .http.views.health_view import HealthView
from .http.views.iqc_view import iQCView
from .http.views.config_manager_view import ConfigManagerView
from .http.views.cache_manager_view import CacheManagerView

urlpatterns = [
    path('health', HealthView.as_view({'get': 'health'})),
    path('check-iqc-contract', iQCView.as_view({'post': 'check_iqc_contract'})),
    path('toolbar-search-iqc', iQCView.as_view({'get': 'toolbar_search_iqc'})),

    # tab triển khai
    path('load-iqc-album-upload-deployment', iQCView.as_view({'post': 'load_iqc_album_upload_deployment'})),
    path('get-iqc-detail-deployment', iQCView.as_view({'post': 'get_iqc_detail_deployment'})),
    path('create-contract-deployment', iQCView.as_view({'post': 'create_contract_deployment'})),
    path('update-contract-deployment', iQCView.as_view({'post': 'update_contract_deployment'})),

    # tab hạ tầng ngoại vi
    path('load-iqc-upload-practice-point', iQCView.as_view({'post': 'load_iqc_upload_practice_point'})),
    path('load-iqc-detail-practice-point', iQCView.as_view({'post': 'load_iqc_detail_practice_point'})),
    path('create-practice-point', iQCView.as_view({'post': 'create_practice_point'})),
    path('update-practice-point', iQCView.as_view({'post': 'update_practice_point'})),
    path('practice-point-get-cause-image', iQCView.as_view({'get': 'practice_point_get_cause_image'})),
    path('get-practice-point-search', iQCView.as_view({'get': 'get_practice_point_search'})),
    path('get-practice-point-check-version', iQCView.as_view({'get': 'get_practice_point_check_version'})),

    # tab hợp đồng trả về
    path('load-iqc-upload-return-contract', iQCView.as_view({'post': 'load_iqc_upload_return_contract'})),
    path('load-iqc-detail-return-contract', iQCView.as_view({'post': 'load_iqc_detail_return_contract'})),
    path('create-or-update-return-contract', iQCView.as_view({'post': 'create_or_update_return_contract'})),

    # các aapi get list danh sách text-box
    path('get-list-house-model', iQCView.as_view({'get': 'get_list_house_model'})),
    path('get-list-transaction-type', iQCView.as_view({'get': 'get_list_transaction_type'})),
    path('get-list-return-contract-cause', iQCView.as_view({'get': 'get_list_return_contract_cause'})),

    path('upload-image', iQCView.as_view({'post': 'upload_image'})),
    # path('upload-image', iQCView.as_view({'post': 'upload_image_new'})),

    # api chỉ để gọi nội bộ
    path('update-mock-all-account-MBN', iQCView.as_view(
        {'post': 'update_mock_all_account_MBN', 'get': 'update_mock_all_account_MBN',
         'delete': 'update_mock_all_account_MBN'})),
    path('get-all-config', ConfigManagerView.as_view({'get': 'get_all_config'})),
    path('get-config-value-by-key', ConfigManagerView.as_view({'post': 'get_config_value_by_key'})),
    path('add-or-update-config-by-key', ConfigManagerView.as_view({'post': 'add_or_update_config_by_key'})),
    path('get-all-cache', CacheManagerView.as_view({'get': 'get_all_cache'})),
    path('get-cache-value-by-key', CacheManagerView.as_view({'post': 'get_cache_value_by_key'})),
    path('clear-cache-by-key', CacheManagerView.as_view({'post': 'clear_cache_by_key'})),
    path('clear-cache-by-prefix', CacheManagerView.as_view({'post': 'clear_cache_by_prefix'}))
]
