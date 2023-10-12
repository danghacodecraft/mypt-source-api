from project.celery import app
from ..serializers.tool_serializer import ToolSerializer
from ...configs.variable_system import NO_PROXY, HEADERS_DEFAULT,STATUS_TOOLS, EXPIRE_TOOL_STATUS,TAB_TOOLS_CONDITION, HOME_STATUS
from ...configs.service_api_config import get_api_info
from ...core.helpers.helper import keys_snake_to_camel
import requests


@app.task
def create_tools(email):
    try:
        response = requests.request(
            **get_api_info("SCM", "tools"),
            params={
                "email": str(email).lower()
            },
            headers=HEADERS_DEFAULT,
            proxies=NO_PROXY
        )
        response = response.json()
        
        data_save = keys_snake_to_camel(response['ListData'])
            
        serializer = ToolSerializer(data=data_save, many=True)
        if serializer.is_valid():
            serializer.save()
        return "OK"
    except Exception as e:
        return str(e)