import json
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request

from app.core.helpers.auth_session_handler import getUserAuthSessionData
from ..models.service_logger import ServiceLogger
from ..serializers.service_logger_serializer import ServiceLoggerSerializer
import warnings

class ServiceLoggerViewSet(ViewSet):
    def record_action(self, request=None, context={} ,result="success"):
        try:
            # if not isinstance(result, str):
            #     warnings.warn("'result' expected is Str")
                
            _data = {
                "result": result if isinstance(result, str) else str(result)
            }
            
            if isinstance(request, Request):
                _data['path'] = request.get_full_path().replace("/mypt-setting-api/v1/", "")
                authorization_data = request.headers.get("Authorization", None)
                session_data = getUserAuthSessionData(authorization_data)
                if session_data is None:
                    _data['user_id'] = None
                else:
                    _data['user_id'] = session_data['userId']
                    
                _data['data'] = request.data
                _data['params'] = request.GET
                _data['headers'] = dict(request.headers)
                
            else:
                _data['path'] = context.get("path", "UNKNOWN")
                if "UNKNOWN" == _data['path']:
                    warnings.warn("Cron Service Warning: Argument 'context' no has key 'path'")
                
            serializer = ServiceLoggerSerializer(data=_data)
            
            if serializer.is_valid():
                serializer.save()
                return True
            
            print(serializer.errors)
            return False
    
        except Exception as e:
            print(e)
            return False
