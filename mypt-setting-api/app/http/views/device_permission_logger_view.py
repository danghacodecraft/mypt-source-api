from datetime import datetime
from rest_framework.viewsets import ViewSet

from app.core.helpers.auth_session_handler import getUserAuthSessionData
from ...core.helpers.response import response_data
from ..validation.device_permission_validator import *
from ..serializers.device_permission_serializer import *
from django.db import connections

class DevicePermissionsViewSet(ViewSet):
    def add_new_device_permission(self, request):
        try:
            data = request.data
            validate = DevicePermissionsValidator(data=data)
            if not validate.is_valid():
                return response_data(statusCode=4, message=validate.errors)  
            
            new_per = DevicePermissionsSerializer(data=data)
            if new_per.is_valid():
                try:
                    new_per.save()
                    return response_data(new_per.data)
                except:
                    return response_data(statusCode=4, message="Permission Code Already Exists")
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")
        else:
            return response_data(new_per.errors, statusCode=4, message="Save Failure")
        
    def get_device_permissions_info(self, request):
        try:
            query_params = request.GET
            
            if "all" in query_params and "true" == query_params['all']:
                queryset = DevicePermissions.objects.all()
            else:
                queryset = DevicePermissions.objects.filter(is_active=True)
                
            serializer = DevicePermissionsSerializer(queryset, many=True)
            return response_data(serializer.data)

        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")
        
    def remove_device_permission(self, request):
        try:
            payload = request.data
            permission_code = payload.pop("permission_code", None)
            
            if permission_code:
                try:
                    queryset = DevicePermissions.objects.get(permission_code=permission_code)
                except:
                    return response_data(statusCode=4, message="Permission Doesn't Exists")
                queryset.is_active = False
                queryset.save()
                return response_data()

        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")
                 
class DevicePermissionLoggerViewSet(ViewSet):
    def filtering(self, conditions):
        queryset = DevicePermissionLogger.objects.all()
            
        if "user_id" in conditions:
            queryset = queryset.filter(user_id=conditions["user_id"])
        if "permission" in conditions:
            queryset = queryset.filter(permission=conditions["permission"])
        if "status" in conditions:
            queryset = queryset.filter(status=conditions["status"])
        if "timeline" in conditions:
            timeline = conditions["timeline"]
            time_format = "%Y/%m/%d"
            try:
                previous_time = datetime.strptime(timeline.get("previous_time", "0001/01/01"), time_format)
                later_time = datetime.strptime(timeline.get("later_time", "9999/12/31"), time_format)
            except Exception as e:
                print(e)
                return False
            
            queryset = queryset.filter(log_at__date__gte=previous_time)
            queryset = queryset.filter(log_at__date__lte=later_time)
        
        return queryset
    
    def add_log(self, request):
        try:
            session_data = getUserAuthSessionData(request.headers.get("Authorization"))
            if session_data is None:
                return response_data(statusCode=4, message="Server Error")
                
            user_id = session_data['userId']
            data = request.data
            data['user_id'] = user_id
            validate = DevicePermissionLoggerValidator(data=data)
            
            if not validate.is_valid():
                return response_data(statusCode=4, message=validate.errors)  
            
            try:
                DevicePermissions.objects.get(permission_code=data.get('permission', "Unknown"))
            except:
                return response_data(statusCode=4, message="Invalid Permission Code")  
            
            serializer = DevicePermissionLoggerSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                
                data['status_after_change'] = data.pop("status", 0)
                verifier = self.add_or_update_one_last_change(data)
                if verifier[1]:
                    return response_data(serializer.data)  
                else:
                    return response_data(serializer.data, statusCode=4, message="Unable To Save The Last State")  
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")
        else:
            return response_data(serializer.errors, statusCode=4, message="Save Failure")
          
    def get_logs(self, request):
        try:
            conditions = request.data
            queryset = self.filtering(conditions)
            for conn in connections.all():
                print(conn)
            
            if False == queryset:
                return response_data(statusCode=4, message="Time Data Doesn't Match Format '%Y/%m/%d'")
            
            serializer = DevicePermissionLoggerSerializer(queryset, many=True)
            return response_data(serializer.data)
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")
           
    def clear_logs(self, request):
        try:
            conditions = request.data
            verifier  = ("user_id" in conditions) \
                            or ("permission" in conditions) \
                            or ("status" in conditions) \
                            or ("timeline" in conditions) \
                            or ("all" in conditions)
                            
            if not verifier:
                return response_data(statusCode=5, message="Want To Delete Them All? Please Add 'all: true' To Execute!")
            
            if "all" in conditions:
                all = conditions["all"]
                
                if True == all:
                    queryset = self.filtering({})
                else:
                    return response_data(statusCode=5, message="Want To Delete Them All? Please Add 'all: true' To Execute!")
            else:
                queryset = self.filtering(conditions)
            
            if False == queryset:
                return response_data(statusCode=4, message="Time Data Doesn't Match Format '%Y/%m/%d'")
            
            res = queryset.delete()
            return response_data()
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")
 
    def export_report(self, request):
        try:
            conditions = request.data
            queryset = self.filtering(conditions)
            
            if False == queryset:
                return response_data(statusCode=4, message="Time Data Doesn't Match Format '%Y/%m/%d'")
            
            serializer = DevicePermissionLoggerSerializer(queryset, many=True)
            data = serializer.data
            # export_file = json_to_excel(data, "data.xlsx")
            export_report = False
            if export_report:
                return response_data(serializer.data)
            else:
                return response_data(statusCode=4, message="Coming soon.....")
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")
    
    def add_or_update_one_last_change(self, data):
        validate = DevicePermissionLastChangeValidator(data=data)
            
        if not validate.is_valid():
            return validate.errors, False
        
        try:
            DevicePermissions.objects.get(permission_code=data.get('permission', "Unknown"))
        except:
            return "Invalid Permission Code", False
        
        current_change = DevicePermissionLastChange.objects.filter(
                                                            user_id=data['user_id'], 
                                                            permission=data['permission']
                                                        ).first()
        
        if current_change:
            current_change.status_after_change = data['status_after_change']
            current_change.save()
            serializer = DevicePermissionLastChangeSerializer(current_change)
            
            return serializer.data, True

        else:
            serializer = DevicePermissionLastChangeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return serializer.data, True
            return serializer.errors, False
    
    def add_or_update_last_change(self, request):
        try:
            session_data = getUserAuthSessionData(request.headers.get("Authorization"))
            if session_data is None:
                return response_data(statusCode=4, message="Server Error")
            
            data = request.data
            user_id = session_data['userId']
            
            if not "logs" in data:
                return response_data(statusCode=4, message="'Logs' is required") 
            
            logs = data.pop('logs', [])
            
            if not isinstance(logs, list):
                return response_data(statusCode=4, message="'Logs' must be a List") 
            
            res_data = []
            
            for log in logs:
                log['user_id'] = user_id 
                verifier = self.add_or_update_one_last_change(log)
                
                if not verifier[1]:
                    return response_data(statusCode=4, message=verifier[0])
                
                res_data.append(verifier[0])
                
            return response_data(res_data)
        except Exception as e:
            print(e)    
            return response_data(statusCode=4, message="Server Error")
     
class DevicePermissionLastChangeView(ViewSet):
    def filtering(self, conditions):
        queryset = DevicePermissionLastChange.objects.all()
            
        if "user_id" in conditions:
            queryset = queryset.filter(user_id=conditions["user_id"])
        if "permission" in conditions:
            queryset = queryset.filter(permission=conditions["permission"])
        if "status_after_change" in conditions:
            queryset = queryset.filter(status_after_change=conditions["status_after_change"])
        if "timeline" in conditions:
            timeline = conditions["timeline"]
            time_format = "%Y/%m/%d"
            try:
                previous_time = datetime.strptime(timeline.get("previous_time", "0001/01/01"), time_format)
                later_time = datetime.strptime(timeline.get("later_time", "9999/12/31"), time_format)
            except Exception as e:
                print(e)
                return False
            
            queryset = queryset.filter(updated_at__date__gte=previous_time)
            queryset = queryset.filter(updated_at__date__lte=later_time)
            
        serializer = DevicePermissionLastChangeSerializer(queryset, many=True)
        
        return serializer.data
           
    def get_logs_last_change(self, request):
        try:
            conditions = request.data
            data = self.filtering(conditions)
            
            if False == data:
                return response_data(statusCode=4, message="Time Data Doesn't Match Format '%Y/%m/%d'")
            return response_data(data)
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")