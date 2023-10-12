from http.models.setting_config_model import SettingConfig
from http.serializers.setting_config_serializer import SettingConfigSerializer
from http.entities import global_data
import json

redis_service = global_data.redis_service

def get_config(config_key, get_from_db=True):
    try:
        config = redis_service.get_value_by_key("SETTING_CONFIGS")['data']
        
        if config != None and config_key in config:
            return config[config_key]
        elif get_from_db:
            config_from_sql = SettingConfig.objects.filter(config_key=config_key, config_status="enabled").first()
            if config_from_sql:
                serializer = SettingConfigSerializer(config_from_sql)
                data = json.loads(serializer.data['config_value'])
                if isinstance(config, dict):
                    config[config_key] = data
                else:
                    config = {
                        config_key: data
                    } 
                redis_service.set_data_by_key("SETTING_CONFIGS", json.dumps(config), 30*24*60*60)
                return data
        else:
            return None
    except Exception as e:
        print(e)
        return None
    else:
        return None

def remove_config(config_key):
    config = redis_service.get_value_by_key("SETTING_CONFIGS")['data']
    if config != None and config_key not in config:
        return True

    config.pop(config_key, None)
    print(config)
    redis_service.set_data_by_key("SETTING_CONFIGS", json.dumps(config))
    
    return True

def set_config(config_key, value):
    if isinstance(value, dict) or isinstance(value, list):
        configs = redis_service.get_value_by_key("SETTING_CONFIGS")['data']
        if not isinstance(configs, dict):
            configs = {}
        configs[config_key] = value
        redis_service.set_data_by_key("SETTING_CONFIGS", json.dumps(configs), 30*24*60*60)
    else:
        raise Exception("value must be a dict or list")
