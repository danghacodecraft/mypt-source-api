from rest_framework.viewsets import ViewSet
from django.core.cache import cache

from app.http.validations.cache_validator import KeyValidate
from ..serializers.tool_serializer import ToolSerializer
from ..models.tools import Tools
from core.helpers.response import *
from ..paginations.custom_pagination import StandardPagination
from datetime import datetime, timedelta
import requests
from app.configs.service_api_config import get_api_info
import json
from ...configs.variable_system import NO_PROXY, HEADERS_DEFAULT,STATUS_TOOLS, EXPIRE_TOOL_STATUS,TAB_TOOLS_CONDITION, HOME_STATUS
from ...configs.variable_response import *
from core.helpers.helper import keys_snake_to_camel
from django.core.cache import cache
from core.helpers.auth_session_handler import getUserAuthSessionData
from datetime import datetime
from ..tasks.create_tools_from_scm import create_tools as ct_scm

class  ToolView(ViewSet):
    paginator = StandardPagination()
    
    def show_tools(self, request):
        try:
            self.add_tools(request=request)
            data = request.GET.copy()
            header_data = request.headers.get("Authorization", "")
            user_data = getUserAuthSessionData(header_data)
            user_email = user_data.get("email", "").lower()
            queryset = Tools.objects.filter(email=user_email) 
            tab_tool = data.get("tab")
            if tab_tool in list(TAB_TOOLS_CONDITION.keys()):
                queryset = queryset.filter(**self.status_tool(tab_tool=tab_tool))
            elif "id" in data and data['id'] not in ["", None]:
                queryset = queryset.filter(id=data['id'])
            serializer = ToolSerializer(queryset, many=True, status_message=True)
            return self.list_tab(user_email,data=serializer.data)
        except:
            return self.list_tab(user_email, data=[])
        
    def status_tool(self, tab_tool) -> dict:
        delta = datetime.now()
        condition = {}
        for item in TAB_TOOLS_CONDITION.get(tab_tool, []):
            condition.update({
                item['condition']: (delta + timedelta(days=item['number'])).strftime('%Y-%m-%d')
            })
        return condition
        
    def add_tools(self, request):
        header_data = request.headers.get("Authorization", "")
        user_data = getUserAuthSessionData(header_data)
        user_email = user_data.get("email", "").lower()
        debound = cache.get(version='call_scm_tool', key=user_email)
        if debound is None:
            try:
                ct_scm.apply_async(kwargs={"email":user_email})
                cache.set(version='call_scm_tool', key=user_email, value="1", timeout=100)
                return response_data()
            except Exception as e:
                return response_data(
                    status=STATUS.ERROR_SYSTEM.value,
                    message=ERROR_MESSAGE.SYSTEM.value
                )
        return response_data()
    
    
    def count_tools_expiration(self, request):
        header_data = request.headers.get("Authorization", "")
        user_data = getUserAuthSessionData(header_data)
        user_email = user_data.get("email", "").lower()
        queryset = Tools.objects.filter(email=user_email)
        expiration = queryset.filter(**self.status_tool('EXPIRED'))
        about_to_expiration = queryset.filter(**self.status_tool('ABOUT_TO_EXPIRED'))
        about_to_expiration = queryset.filter(**self.status_tool('ALL'))
        return self.list_tab(
            user_email,
            status_tool=HOME_STATUS,
            data={
                    "expiration":{
                        "number":expiration.count(),
                        "text": getattr(STATUS_TOOLS, "EXPIRED").value,
                        "key": "EXPIRED"
                    },
                    "aboutToExpire":{
                        "number":about_to_expiration.count(),
                        "text": getattr(STATUS_TOOLS, "ABOUT_TO_EXPIRED").value,
                        "key": "ABOUT_TO_EXPIRED"
                    }
                }
            )
        
    def list_tab(self, email,data={}, status_tool=STATUS_TOOLS):
        queryset = Tools.objects.filter(email=email)
        list_tab = [{\
            'name': member.value,\
            'keyTab':str(member.name),\
            'number':queryset.filter(**self.status_tool(str(member.name))).count()\
            if member.name != "NO_EXPIRED" else queryset.filter(**self.status_tool(str(member.name))).count()\
            + queryset.filter(expire_date__isnull=True).count()\
            } for member in status_tool\
        ]
        return response_data(
            data={
                "listTab":list_tab,
                "listData":data
            }
        )
        
    def call_scm(self, request):
        queryset = Tools.objects.filter().values_list('email', flat=True)
        list_email = set(queryset)
        for item in list_email:
            ct_scm.apply_async(kwargs={"email":item})
        return response_data(list_email)
        
        
    def test_create(self, request):
        try:
            data = request.data.copy()
            # data = {
            #     "scmId": request.data["scmId"],
            #     "itemCode": "ABCFGE",
            #     "itemName": "Kìm kẹp",
            #     "sizeName": "",
            #     "assetCode": "",
            #     "stockName": "kho hàng cấp 2.1",
            #     "zoneName": "Hàng mất",
            #     "email": "anph13@fpt.com",
            #     "serial": "38123321",
            #     "quantityNow": 100,
            #     "quantityHold": 0,
            #     "startDate": "13/07/2023",
            #     "expireDate": request.data["date"]
            # }
            
            serializer = ToolSerializer(data=data)

            if not serializer.is_valid():
                return response_data(serializer.errors)
            
            serializer.save()
            
            return response_data(serializer.data)
        except Exception as e:
            print(e)
            return response_data(str(e))
    
    def view_cache(self, request):
        return response_data(cache.keys("*"))