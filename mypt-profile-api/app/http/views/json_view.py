from rest_framework.viewsets import ViewSet
import json
import requests

from ...configs.variable import PROXIES
from ..validations.json_validate import *
from ...core.helpers.response import *

class JsonView(ViewSet):
    def call_api(self, url):
        payload={}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload, proxies=PROXIES)
        return (response.text)
        
    def task_kpi(self, request):
        url = "https://firebasestorage.googleapis.com/v0/b/my-pt-pnc.appspot.com/o/kpi.json?alt=media&token=f844d07d-7b6c-4245-8acc-fd3f1f90b1e1"
        data = request.data.copy()
        try:
            validate = CaseValidate(data=data)
            if not validate.is_valid():
                return response_data(status=5, message=validate.errors, data={})
            data_api = self.call_api(url=url)
            data_api = json.loads(data_api)
            for item in data["case"]:
                data_api = data_api[item]
            return response_data(data_api)
        except Exception:
            return response_data(status=4, message="lỗi input truyền vào", data={})