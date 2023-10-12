# from django.dispatch import receiver
# from django.db.backends.signals import connection_created

from http.views.cron_view import CronViewSet
from http.views.email_service_view import EmailReportViewSet

# @receiver(connection_created)
# def execute_after_connected_to_database(connection, **kwargs):
#     print("--------- @receiver(connection_created)------------")
    

def run_once():
    print("------------- RUN ONCE -------------")
    CronViewSet().cron_initial()
    EmailReportViewSet().email_initial()
    return True

run_once()