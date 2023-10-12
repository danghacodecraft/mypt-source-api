from django.core.cache import cache
from app.http.models.job_configs import JobConfigs
from app.http.serializers.job_configs_serializer import JobConfigsSerializer

class ConfigManager():
    @staticmethod
    def get_and_cache(key, timeout=24*60*60):
        try:
            value = cache.get(key=f"configs:{key}", default=None)

            if value is None:
                try:
                    instance = JobConfigs.objects.get(key=key)
                except Exception as e:
                    print("config does not exist!")
                
                value =  JobConfigsSerializer(instance).data["config_value"]
                cache.set(key=f"configs:{key}", value=value, timeout=timeout)
                
            return value
        except Exception as e:
            print(e)
            return None
    
    @staticmethod
    def refresh(key, timeout=24*60*60):
        try:
            old_value = cache.get(key=f"configs:{key}", default=None)

            try:
                instance = JobConfigs.objects.get(key=key)
            except Exception as e:
                print("config does not exist!")
            
            new_value = JobConfigsSerializer(instance).data["config_value"]
            cache.set(key=f"configs:{key}", value=new_value, timeout=timeout)
                
            return {"old_value": old_value, "new_value": new_value}
        except Exception as e:
            print(e)
            return None
       
    @staticmethod 
    def all():
        return cache.get_many(cache.keys("*"))