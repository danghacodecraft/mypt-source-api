from ..entities import global_data
from core.helpers.response import *
from core.helpers.utils import *
# from ..paginations.custom_pagination import *
from rest_framework.viewsets import ViewSet
from datetime import *
import json
from mimetypes import guess_extension

from ..serializers.storage_uuid_serializer import *
from ..serializers.list_folder_serializer import *

from core.helpers import auth_session_handler as authSessionHandler


class UploadFile(ViewSet):
    def upload_file(self, request):

        fname = "upload_file_private"

        # lay tu token
        # data_token = global_data.authUserSessionData
        data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        user_email = data_token.get("email", "")

        # ===================
        # lay tu input
        data_input = request.data
        folder = data_input.get("folder", '')
        upload_type = data_input.get("uploadType", None)

        if is_null_or_empty(upload_type):
            upload_type = "DEFAULT"
        else:
            if upload_type not in MESSAGE_UPLOAD_TYPE:
                return response_data(data={},
                                     message="Loại upload không hợp lệ.",
                                     status=STATUS_CODE_INVALID_INPUT)

        if is_null_or_empty(user_email):
            return response_data(data={}, message="Token khong phu hop", status=STATUS_CODE_INVALID_INPUT)

        if is_null_or_empty(folder):
            return response_data(data={}, message="Vui lòng cho biết thông tin tên thư mục",
                                 status=STATUS_CODE_INVALID_INPUT)

        # if folder not in ['che_tai']:

        try:
            if not ListFolder.objects.filter(folder=folder).exists():
                return response_data(data={}, message="Sai tên thư mục",
                                     status=STATUS_CODE_INVALID_INPUT)

            data = {}
            dict_upload = upload_file(request=request,
                                      user_email=user_email,
                                      folder_name=folder,
                                      fname=fname,
                                      upload_type=upload_type)
            ok = dict_upload.get("ok", False)
            if ok:
                link_public = dict_upload.get("link_public", [])
                file_name = dict_upload.get("file_name", [])
                data.update({
                    "fileName": file_name,
                    "linkFile": link_public
                })
                print("THANH CONG TRA VE DATA ------------------------------")
                print(data)
                return response_data(data=data, status=STATUS_CODE_SUCCESS,
                                     message=MESSAGE_UPLOAD_TYPE[upload_type]["success_message"])
            else:
                msg = dict_upload['message']
                status_api = STATUS_CODE_ERROR_LOGIC
                return response_data(data=data, status=status_api, message=msg)
        except Exception as ex:
            print("{} >> Error/Loi: {}".format(fname, ex))
            return response_data(data={},
                                 message=MESSAGE_UPLOAD_TYPE[upload_type]["error_messages"]["failed"],
                                 status=STATUS_CODE_ERROR_LOGIC)

    def upload_file_private(self, request):

        fname = "upload_file_private"
        # ===================
        # lay tu input
        data_input = request.data
        user_email = data_input.get("userEmail", '')
        folder = data_input.get("folder", '')
        if is_null_or_empty(folder):
            return response_data(data={}, message="Vui lòng cho biết thông tin tên thư mục",
                                 status=STATUS_CODE_INVALID_INPUT)

        try:
            data = {}
            dict_upload = upload_file(request=request, user_email=user_email, folder_name=folder, fname=fname)
            ok = dict_upload.get("ok", False)
            if ok:
                link_public = dict_upload.get("link_public", [])
                file_name = dict_upload.get("file_name", [])
                data.update({
                    "fileName": file_name,
                    "linkFile": link_public
                })
                print("THANH CONG TRA VE DATA ------------------------------")
                print(data)
                return response_data(data=data, status=STATUS_CODE_SUCCESS, message=MESSAGE_API_SUCCESS)
            else:
                msg = "Up file thất bại"
                status_api = STATUS_CODE_ERROR_LOGIC
                return response_data(data=data, status=status_api, message=msg)
        except Exception as ex:
            print("{} >> Error/Loi: {}".format(fname, ex))
            return response_data(data={}, message=MESSAGE_API_FAILED, status=STATUS_CODE_ERROR_LOGIC)
