import json

import requests

from ..entities import global_data
from ...core.helpers.response import *
from ...core.helpers.utils import *
from ...core.helpers import auth_session_handler as authSessionHandler
from ...configs.app_settings import AES_SECRET_KEY
# from ..paginations.custom_pagination import *
from rest_framework.viewsets import ViewSet
from ..serializers.list_folder_serializer import *

import mimetypes

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from rest_framework import status
from rest_framework.response import Response

from django.shortcuts import redirect
from datetime import datetime
from django.http import HttpResponsePermanentRedirect


class ShowFile(ViewSet):
    def show_file(self, request):
        path = request.GET['path']
        # path = data_input.get("path", "")
        # print("------------------")
        # print(path)


        # Define text file name
        # filename = '20220608_141932_test_new_1.jpg'
        # filename_split = path.split("/")
        # filename = filename_split[len(filename_split) - 1]

        # Define the full file path
        # filepath = BASE_DIR + '/filedownload/Files/' + filename
        # filepath = "D:\\home\\cds\\my_TIN_PNC\\mytin_backend\\data\\upload\\thu_vien\chinh_sach\\20220608_141932_test_new_1.jpg"
        # filepath = FOLDER_PATH + "/" + path
        try:

            test_input = int(path)

            queryset = StorageUuid.objects.filter(uuid=path)
            serializer = StorageUuidSerializer(queryset, many=True, fields=['linkLocal'])
            print(queryset.query)
            list_data = serializer.data
            if len(list_data) == 0:
                return response_data(data={}, message="Không tìm thấy data", status=STATUS_CODE_NO_DATA)

            filepath = list_data[0]['linkLocal']

            # Open the file for reading content
            path = open(filepath, 'rb')

            # Set the mime type
            mime_type, tmp = mimetypes.guess_type(filepath)

            # Set the return value of the HttpResponse
            response = HttpResponse(path, content_type=mime_type)

            # Set the HTTP header for sending to browser
            # response['Content-Disposition'] = "attachment; filename=%s" % filename
            # Return the response value
            return response
        except Exception as ex:
            print(
                "---------------------------showfile------------------------------------------------------------------")
            print(ex)
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_FAILED)

    def show_file_auth(self, request):
        if "path" not in request.GET:
            return HttpResponseNotFound("Đường dẫn không hợp lệ!")
        path = request.GET['path']
        path = path.replace(" ", "+")

        path = decrypt_aes(AES_SECRET_KEY, path)
        str_list = path.split(";")
        path = str_list[0]
        owner = str_list[1]

        user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        if not str(user_token["userId"]) == owner:
            return HttpResponseForbidden("Bạn không có quyền!")

        try:
            test_input = int(path)

            queryset = StorageUuid.objects.filter(uuid=path)
            serializer = StorageUuidSerializer(queryset, many=True, fields=['linkLocal'])
            print(queryset.query)
            print('path: ', path)
            print('owner: ', owner)
            list_data = serializer.data
            if len(list_data) == 0:
                return HttpResponseNotFound("Đường dẫn không hợp lệ !")

            filepath = list_data[0]['linkLocal']

            # Open the file for reading content
            path = open(filepath, 'rb')

            # Set the mime type
            mime_type, tmp = mimetypes.guess_type(filepath)

            # Set the return value of the HttpResponse
            response = HttpResponse(path, content_type=mime_type)

            # Set the HTTP header for sending to browser
            # response['Content-Disposition'] = "attachment; filename=%s" % filename
            # Return the response value
            return response
        except Exception as ex:
            print(
                "---------------------------showfile------------------------------------------------------------------")
            print(ex)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def show_image_iqc(self, request):
        try:
            if "path" not in request.GET:
                return HttpResponseNotFound("Đường dẫn không hợp lệ!")
            path = request.GET['path']
            path = path.replace(" ", "+")

            path = decrypt_aes(AES_SECRET_KEY, path)
            str_list = path.split(";")
            path = str_list[0]
            owner = str_list[1]

            user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            if not str(user_token["userId"]) == owner:
                return HttpResponseForbidden("Bạn không có quyền!")

            return HttpResponsePermanentRedirect(path)
        except Exception as ex:
            print(f"{datetime.now()} >> show_image_iqc >> {ex}")
            return HttpResponseNotFound("Đường dẫn không hợp lệ!")


