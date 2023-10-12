from django.urls import path

from .http.views.build_house_model_view import BuildCusHomeModelView
from .http.views.cache_manager_view import CacheManagerView
from .http.views.current_contract_info_log_view import CurrentContractInfoLogView
from .http.views.health_view import *
from .http.views.proposed_equipment_view import ProposedEquipmentView
from .http.views.survey_view import CusHomeModelSurveyView
from .http.views.views import CusHomeModelView

urlpatterns = [
    # những api test kết nối
    path('health', HealthView.as_view({'get': 'health'})),
    path('get-api', HealthView.as_view({'get': 'add_kong'})),

    path('calculate-model-equipment', CusHomeModelView.as_view({'post': 'calculate_model_equipment'})),
    path('types-models', CusHomeModelView.as_view({'get': 'get_types_model'})),
    path('get-templates', CusHomeModelView.as_view({'get': 'get_template_model'})),
    path('current-equipments-info-list', CusHomeModelView.as_view({'post': 'current_equipments_info_list'})),
    path('transform-image', CusHomeModelView.as_view({'post': 'transform_image'})),

    # api thiết bị đề xuất
    path('list-proposed-equipment', ProposedEquipmentView.as_view({'get': 'list'})),
    path('create-proposed-equipment', ProposedEquipmentView.as_view({'post': 'create'})),

    # lưu, cập nhật, xem chi tiết và danh sách thông số khảo sát
    path('create-model-survey', CusHomeModelSurveyView.as_view({'post': 'post_create_custom_house_model_survey'})),
    path('update-model-survey', CusHomeModelSurveyView.as_view({'post': 'post_update_custom_house_model_survey'})),
    path('get-history-model-survey', CusHomeModelSurveyView.as_view({'post': 'get_history_model_survey'})),
    path('get-detail-model-survey', CusHomeModelSurveyView.as_view({'post': 'get_detail_model_survey'})),
    path('get-current-model-survey', CusHomeModelSurveyView.as_view({'post': 'get_current_version_survey'})),

    # tạo, xem mô hình nhà KH
    # path('create-house-model', BuildCusHomeModelView.as_view({'post': 'post_create_house_model'})),
    path('update-house-model', BuildCusHomeModelView.as_view({'post': 'post_update_house_model'})),
    path('current-house-model', BuildCusHomeModelView.as_view({'post': 'get_current_house_model'})),
    path('detail-house-model', BuildCusHomeModelView.as_view({'post': 'get_detail_house_model'})),

    path('get-all-cache', CacheManagerView.as_view({'post': 'get_all_cache'})),
    path('clear-db-cache', CacheManagerView.as_view({'delete': 'clear_db_cache'})),
    # path('clear-db-cache', CacheManagerView.as_view({'post': 'clear_db_cache'})),

    # danh sách, hợp đồng hiện trạng
    path('list-current-contract-info-log', CurrentContractInfoLogView.as_view({'post': 'list'})),

    # decode image base64
    path('decode-image-base64', CusHomeModelView.as_view({'post': 'decode_image_base64'})),

    # api test
    path('test-api', CusHomeModelView.as_view({'post': 'test_api'}))
]
