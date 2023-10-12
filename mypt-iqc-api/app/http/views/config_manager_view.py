import json
from datetime import datetime
from django.db import transaction
from rest_framework.viewsets import ViewSet
from ...http.models.iqc_config import IqcConfig
from ...core.helpers import global_variable
from ...core.helpers.response import response_data


class ConfigManagerView(ViewSet):
    def get_all_config(self, request):
        try:
            all_iqc_config = IqcConfig.objects.values()
            return response_data(all_iqc_config)
        except Exception as ex:
            print(f"{datetime.now()} >> get_all_config >> {ex}")
            return response_data(status=global_variable.STATUS_CODE_ERROR_SYSTEM,
                                 message=global_variable.MESSAGE_API_ERROR_SYSTEM)

    def get_config_value_by_key(self, request):
        data = request.data.copy()
        try:
            if "configKey" not in data:
                return response_data(status=global_variable.STATUS_CODE_INVALID_INPUT,
                                     message="configKey là bắt buộc!")
            config_key = data["configKey"]
            if not config_key:
                return response_data(status=global_variable.STATUS_CODE_INVALID_INPUT,
                                     message="configKey không hợp lệ!")
            config_values = IqcConfig.objects.filter(config_key=config_key).values("config_value")
            if len(config_values) > 0:
                return response_data(data={
                    f"{config_key}": config_values[0]["config_value"]
                })
            return response_data(status=global_variable.STATUS_CODE_NO_DATA,
                                 message=global_variable.MESSAGE_API_NO_DATA)
        except Exception as ex:
            print(f"{datetime.now()} >> get_config_value_by_key >> {ex}")
            return response_data(status=global_variable.STATUS_CODE_ERROR_SYSTEM,
                                 message=global_variable.MESSAGE_API_ERROR_SYSTEM)

    def add_or_update_config_by_key(self, request):
        data = request.data.copy()
        try:
            if "key" not in data:
                return response_data(status=global_variable.STATUS_CODE_INVALID_INPUT,
                                     message="key là bắt buộc!")
            if "value" not in data:
                return response_data(status=global_variable.STATUS_CODE_INVALID_INPUT,
                                     message="value là bắt buộc!")
            key = data["key"]
            value = data["value"]
            if not key:
                return response_data(status=global_variable.STATUS_CODE_INVALID_INPUT,
                                     message="key không hợp lệ!")

            _, created = IqcConfig.objects.update_or_create(
                config_key=key,
                defaults={
                    "config_value": value
                }
            )
            if created:
                return response_data(message=f"Tạo mới thành công!")
            else:
                return response_data(message=f"Cập nhật thành công!")

        except Exception as ex:
            print(f"{datetime.now()} >> update_config_by_key >> {ex}")
            return response_data(status=global_variable.STATUS_CODE_ERROR_SYSTEM,
                                 message=global_variable.MESSAGE_API_ERROR_SYSTEM)