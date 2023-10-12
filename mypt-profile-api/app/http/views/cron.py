from asyncio import Task
from rest_framework.viewsets import ViewSet

from profile_app.core.helpers.response import response_data
from ...cron import *

class Cron(ViewSet):
    tasks = MYPTCron()
    def task(self):
        print(datetime.now())
    def task1(self):
        print(datetime.now()) 
    def cron_start(self, request):
        self.tasks.stop()
        self.tasks.add_job(self.task, '* * * * * */5')
        self.tasks.add_job(self.task1, '* * * * * */5')
        self.tasks.start()
        
        return response_data()