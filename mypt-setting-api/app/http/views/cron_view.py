import json
import requests
from app.core.helpers.response import response_data
from ..models.cron_model import Cron
from ..serializers.cron_serializer import CronSerializer
from ..serializers.call_api_serializer import CallAPILoggerSerializer
from rest_framework.viewsets import ViewSet
from ...core.helpers.schedule import CronBase
from ...core.helpers.string_to_int_representation import string_to_int_representation
from django.conf import settings
from django.db import close_old_connections

cron_api = CronBase()
cron_api.start()    
class CronViewSet(ViewSet):
    def cron_initial(self, request=None):
        try:
            print("------> cron_initial")
            queryset = Cron.objects.filter(is_done=False)
            serializer = CronSerializer(queryset, many=True)
            data = serializer.data
            
            for d in data:
                cron_api.add_task(
                    self.call_api_handler, 
                    d['schedule'], 
                    d['name'],
                    data=d
                )
            return response_data()
        except Exception as e:
            print(e)
            return response_data(statusCode=4)
    
    def get_task_info(self, request):
        try:
            id = request.data.get("id", None)
            name = request.data.get("name", None)
            
            if id is None and name is None:
                return response_data(statusCode=4, message="must have 'name' or 'id'")
            
            if id:
                queryset = Cron.objects.get(id=id)
            else:
                queryset = Cron.objects.get(name=name)
                
            serializer = CronSerializer(queryset)
            return response_data(serializer.data)
        except Exception as e:
            return response_data(statusCode=4, message=str(e))
    
    def add_new_task(self, request):
        try:
            data = request.data
            if "name" not in data:
                data['name'] = self.name_generator(data)
            serializer = CronSerializer(data=data)
            
            if serializer.is_valid():
                _data = serializer.validated_data
                
                if (settings.APP_ENV == "production" and "-staging" in _data["url"]) or \
                    (settings.APP_ENV == "staging" and "-staging" not in _data["url"]):
                    return response_data(statusCode=4, message="Invalid Domain Name")
                
                cron_verifier = cron_api.add_task(
                    self.call_api_handler, 
                    _data['schedule'], 
                    _data['name'],
                    data=_data
                )
                
                if cron_verifier[0]:
                    serializer.save()
                    return response_data()
                return response_data(statusCode=4, message=cron_verifier[1])
            return response_data(statusCode=4, message=serializer.errors)
        except Exception as e:
            print("---", e)
            return response_data(statusCode=4, message=str(e))
           
    def call_api(self, data):
        try:
            method = data.get("method", "get")
            url = data.get("url", "")
            params = data.get("params", None)
            payload = data.get("data", None)
            headers = data.get("headers", None)
            proxies = data.get("proxies", None)
            
            data_to_save = {
                "method": method,
                "url": url,
                "params": params,
                "payload": payload,
                "headers": headers,
                "result": ""
            }
            
            print(f"calling url: {url}")
            
            res = requests.request(
                method=method, 
                url=url,
                params=params,
                data=payload,
                headers=headers,
                proxies=proxies
            )
            print(f"called url: {url}")
            res_data_txt = res.text
            data_to_save['result'] = res_data_txt
            save = CallAPILoggerSerializer(data=data_to_save)
            if save.is_valid():
                save.save()
            print(save.errors)
            print(f"result url {url}: {res_data_txt}")
            try:
                res_data = json.loads(res_data_txt)
                verifier = ("status" in res_data and res_data['status'] == 1)\
                    or ("statusCode" in res_data and res_data['statusCode'] == 1)
                if verifier:
                    print(f"{url} ~~~ {res_data}")
                    return True, res_data
                return False, res_data_txt
            except:
                print(f"{url} ~~~ FALSE")
                return False, res_data_txt
        except Exception as e:
            print(e)
            close_old_connections()
            return False, str(e)
        
    def call_api_handler(self, data):
        def recall_api(data):
            api_res = self.call_api(data)

            if api_res[0]:
                cron_api.clear_task(f"recall_api_{data['name']}")
        
        try:
            cron_api.clear_task(f"recall_api_{data['name']}")
            api_res = self.call_api(data)
            
            if not api_res[0] and bool(data['error_schedule']):
                cron_verifier = cron_api.add_task(
                    recall_api,
                    data['error_schedule'],
                    f"recall_api_{data['name']}",
                    data=data
                )
                return cron_verifier
            
            return True, "success"
        except Exception as e:
            print(e)
            return False, str(e)
    
    def remove_task(self, request):
        try:
            if "name" not in request.data:
                return response_data(statusCode=4, message="'name' is required")
            name = request.data["name"]
            queryset = Cron.objects.get(name=name)
            queryset.is_done = True
            queryset.save()
            cron_api.clear_task(name)
            return response_data()
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message=str(e))
    
    def remove_all_tasks(self, request):
        cron_api.clear_all()
        return response_data()
    
    def name_generator(self, data):
        name = str(string_to_int_representation(str(data)))
        
        if len(name) > 20:
            name = f"{name[:10]}{name[-10:]}"
            
        return name
    
    def refresh(self, request):
        print("cron refresh")
        self.remove_all_tasks(request)
        self.cron_initial()
        return response_data()
    
    def say_hello(self, request):
        try:
            print("say_hello")
            if "content" not in request.data:
                print("'content' is required")
                return response_data(statusCode=4, message="'content' is required")
            
            print(request.data['content'])
            return response_data()
        except Exception as e:
            return response_data(statusCode=4, message=str(e))
        
    def call(self, request):
        try:
            res = self.call_api(request.data)

            if res[0]:
                return response_data(res[1])
            else:
                return response_data(res[1], statusCode=4)
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message=str(e))
        
    def staging_call_to_production(self, request):
        try:
            res = self.call_api(request.data)
            if res[0]:
                return response_data(res[1])
            return response_data(message=res[1], statusCode=4)
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message=f"staging_call_to_production - {str(e)}")