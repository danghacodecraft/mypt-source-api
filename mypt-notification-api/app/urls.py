from django.urls import path
from .http.views.noti_view import *
from .http.views.call_noti import *
from .http.views.health_view import *

urlpatterns = [    
    # path('get-notis-home', getNotisHome),
    path('do-tick', doTick),
    path('do-bell', doBell),
    # path('do-action', doAction),   
    path('health', healthCheck),
    path('send-noti', sendNoti),
    path('send_noti_feedback', NotiView.as_view({'post':'send_noti_feedback'})),
    path('send-noti-pr', NotiView.as_view({'post':'post_send_noti'})),
    path('test-call-pr', NotiView.as_view({'get':'test_call_pr'})),
    path('test-call-pr-noproxy', NotiView.as_view({'get':'test_call_pr_noproxy'})),
    path('time', CallNotiView.as_view({'post':'time_me'})),
    
    path('get-notis-home', NotiView.as_view({'get':'get_noti'})),
    path('get-group-noti', NotiView.as_view({'get':'get_group'})),
    path('do-action', NotiView.as_view({'post':'do_action'})),
    path('service-send-noti', CallNotiView.as_view({'post':'service_send_noti'})),
    path('service-list-code', CallNotiView.as_view({'post':'service_list_code'})),
    path('service-send-muti-noti', CallNotiView.as_view({'post':'send_muti_noti'})),
    
    path('send-multi-noti-with-same-content-by-email', CallNotiView.as_view({'post':'send_multiple_notify_with_the_same_content_by_list_email'})),
    path('send-multi-noti-with-diff-content-by-email', CallNotiView.as_view({'post':'send_multiple_notify_with_the_different_content_by_list_email'})),
    path('update-noti-properties', CallNotiView.as_view({'post':'update_noti_properties'})),
    path('send-one-noti', CallNotiView.as_view({'post':'send_one_noti'})),
    path('cron-send-noti', cron_send_noti),
    path('remove-config', CallNotiView.as_view({'post':'remove_config'})),
    path('get-config', CallNotiView.as_view({'post':'get_config'})),
]

# noti theo employee
# xoá nhiều, đọc nhiều
