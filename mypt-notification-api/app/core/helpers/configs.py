from ...http.models.notification_config import NotificationConfigs
from ...http.serializers.notification_serializer import NotificationConfigsSerializer
from ...http.entities import global_data
import json

redis_service = global_data.redis_service

def get_config(config_key):
    try:
        config = redis_service.get_value_by_key("NOTIFICATION_CONFIGS")['data']
        
        if config != None and config_key in config:
            return config[config_key]
        else:
            config_from_sql = NotificationConfigs.objects.filter(config_key=config_key, config_status="enabled").first()

            if config_from_sql:
                serializer = NotificationConfigsSerializer(config_from_sql)
                data = json.loads(serializer.data['config_value'])
                if isinstance(config, dict):
                    config[config_key] = data
                else:
                    config = {
                        config_key: data
                    } 
                print(config)
                redis_service.set_data_by_key("NOTIFICATION_CONFIGS", json.dumps(config), 30*24*60*60)
                return data
    except Exception as e:
        print(e)
        return None
    else:
        return None

def remove_config(config_key):
    config = redis_service.get_value_by_key("NOTIFICATION_CONFIGS")['data']
    if config != None and config_key not in config:
        return True

    config.pop(config_key, None)
    print(config)
    redis_service.set_data_by_key("NOTIFICATION_CONFIGS", json.dumps(config))
    
    return True
