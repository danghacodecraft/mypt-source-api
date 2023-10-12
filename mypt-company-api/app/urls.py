from django.urls import path

from .http.views.ptq_view import *
from .http.views.health_view import *
from .http.views.improved_car_view import *


urlpatterns = [
    path('health', healthCheck),
    path('list-idea', ImprovedCarView.as_view({'get':'get_list_blog'})),
    path('list-comment', ImprovedCarView.as_view({'get':'get_list_comment'})),
    path('create-blogs', ImprovedCarView.as_view({'post':'post_blog'})),
    path('create-evaluate', ImprovedCarView.as_view({'post':'post_evaluate_idea'})),
    path('create-comment', ImprovedCarView.as_view({'post':'create_comment'})),
    path('edit-comment', ImprovedCarView.as_view({'post':'edit_comment'})),
    path('detele-comment', ImprovedCarView.as_view({'post':'detele_comment'})),
    path('do-like', ImprovedCarView.as_view({'post':'do_like'})),
    # path('send-mail', ImprovedCarView.as_view({'post':'send_email'})),
    path('rate', ImprovedCarView.as_view({'get':'list_group_improved'})),
    path('do-rate', ImprovedCarView.as_view({'get':'get_list_rate', 'post':'post_rate'})),
    path('change-blogs-process-status', ImprovedCarView.as_view({'post': 'change_blogs_process_status'})),

    path('home-count-ptq', PtqView.as_view({'get':'home_count_ptq'})),
    path('home-count-ptq-2', PtqView.as_view({'get':'home_count_ptq_2'})),
    path('history-ptq', PtqView.as_view({'post':'history_ptq'})),
    path('history-ptq-id', PtqView.as_view({'post':'history_ptq_id'})),
    path('ptq-type', PtqView.as_view({'get':'ptq_type'})),
    path('explanation', PtqView.as_view({'post':'explanation'})),
    # path('explanations', PtqView.as_view({'post':'explanations'})),

    # API cho mypt-setting gọi (ẩn hiện tab chế tài)
    path('get-ptq-types-from-redis', PtqView.as_view({'post': 'get_ptq_types_from_redis'})),
    path('get-ptq-from-email', PtqView.as_view({'post': 'get_ptq_from_email'})),
]

