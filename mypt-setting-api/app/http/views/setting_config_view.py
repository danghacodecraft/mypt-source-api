import json
from rest_framework.viewsets import ViewSet
from ..models.setting_config_model import SettingConfig
from ...core.helpers.response import response_data
from ..serializers.setting_config_serializer import SettingConfigSerializer
from ...core.entities.redis_service import RedisService

class SettingConfigViewSet(ViewSet):
    def __init__(self):
        self.redis_service = RedisService()
        
    def set_config(self, request):
        try:
            data = request.data
            
            config_key = data.get("config_key", "UNKNOWN_CONFIG")
            curr_config = SettingConfig.objects.filter(config_key=config_key, config_status="enabled").first()
            
            if curr_config:
                for config in data:
                    setattr(curr_config, config, data[config])
                    
                new_config = curr_config
                curr_config.save()
            else:
                serializer = SettingConfigSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    new_config = serializer.data
                else:
                    return response_data(statusCode=4, message=serializer.errors)
            
            if self.redis_service.health():
                try:
                    key = data['config_key']
                    
                    redis_data_str = self.redis_service.get_value_by_key("SETTING_CONFIGS")['data']
                    
                    if redis_data_str is None:
                        redis_data = {}
                    else:
                        redis_data = json.loads(redis_data_str.replace("'", '"'))
                        
                    if type(new_config).__name__ == SettingConfig.__name__:
                        new_config.__dict__.pop("_state", None)
                        new_config.__dict__.pop("config_id", None)
                        new_config.__dict__["date_created"] = str(new_config.__dict__.get("date_created", ""))
                        new_config.__dict__["date_last_updated"] = str(new_config.__dict__.get("date_last_updated", ""))
                        new_config = new_config.__dict__
                    else:
                        new_config.pop("config_id", None)
                    redis_data[key] = new_config
                    verifier = self.redis_service.set_data_by_key("SETTING_CONFIGS", str(redis_data))
                    
                    if verifier:
                        return response_data()
                except Exception as e:
                    print(e)
            
            return response_data(statusCode=4, message="Redis Error")
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")
        
    def get_config(self, request):
        try:
            data = request.data
            config_key = data.get("config_key", None)
            
            if config_key is None:
                return response_data(statusCode=4, message="'config_key' is required")
            
            config = self.redis_service.get_value_by_key("SETTING_CONFIGS").get("data", None)

            if config_key in config:
                return response_data(data=config[config_key])
            else:
                config_from_sql = SettingConfig.objects.filter(config_key=config_key, config_status="enabled").first()
                
                if config_from_sql:
                    serializer = SettingConfigSerializer(config_from_sql)
                    config_in_db = serializer.data
                    config_in_db['config_value'] = json.loads(config_in_db['config_value'])
                    print("--->", type(config))
                    config[config_key] = config_in_db
                    
                    self.redis_service.set_data_by_key("SETTING_CONFIGS", json.dumps(config))
                    print(2)
                    return response_data(config[config_key])
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")
        else:
            return response_data(data={}, message="Config key doesn't exists")
            
    def remove_config(self, request):
        try:
            data = request.data
            config_key = data.get('config_key', None)
            
            if config_key is None:
                return response_data(statusCode=4, message="'config_key' is required")
            
            redis_data = self.redis_service.get_value_by_key("SETTING_CONFIGS")['data']        
            redis_data.pop(config_key, None)  
            self.redis_service.set_data_by_key(("SETTING_CONFIGS"), json.dumps(redis_data))
            
            return response_data()
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")
