import json
from rest_framework.viewsets import ViewSet
import random
from http.helpers.response import response_data
from ..entities import global_data
import requests
from django.conf import settings
from ..validations.external_login import VerifyOTPValidator
import threading

class ExternalLoginViewSet(ViewSet):
    def sign_up_by_email(self, request):
        try:
            data = request.data.copy()
            if "email" not in data:
                return response_data(statusCode=4, message="'email' is required.")
            
            email = data['email']
            threading.Thread(
                target=self.send_otp_and_save, 
                daemon=True, 
                kwargs={
                    "email": email
                }
            ).start()
            return response_data()
        except Exception as e:
            print(e)
            return response_data(data=str(e), statusCode=4, message="Lỗi hệ thống!")
    
    def generate_otp(self, len):
        otp = ""
        for i in range(len):
            otp = otp + str(random.randint(0,9))
        return otp
    
    def send_otp_and_save(self, email):
        otp = self.generate_otp(4)
        global_data.redis_service.set_data_by_key(f"otp_{email}", otp)
        print(otp)
        suffixes = "-staging" if settings.APP_ENVIRONMENT == "staging" else ""

        res = requests.request(
            "post", 
            f"http://mypt-setting-api{suffixes}/mypt-setting-api/v1/send-email-with-template",
            data={
                "subject": "[MyPT] One Time Password (OTP) Confirmation",
                "template": f'''
                    <div>
                        <div style="background-color:#f0f5fa;">
                            <div style="padding-bottom:10px; padding-top:10px; margin: 0 auto;">
                                <div style="width:100%;">
                                    <img style="text-align:center; padding:25px; width:125px; margin: 0 auto; display: block;" src="https://apis.fpt.vn/mypt-ho-media-api/view-file?path=0172879564639521">
                                </div>
                            </div>
                            <div style="background-color:#fff; padding-bottom:20px; padding-top:20px">
                                <div style="vertical-align:middle; width:100%;">
                                    <div style="text-align:center; font-size:20px; font-family:open Sans Helvetica, Arial, sans-serif; padding-left:25px; padding-right:25px;"><span>Xin chào,</span></div>
                                    <br>
                                    <div style="text-align:center; font-size:20px; font-family:open Sans Helvetica, Arial, sans-serif; padding-left:25px; padding-right:25px;">Vui lòng sử dụng OTP được cung cấp bên dưới để đăng nhập ứng dụng MyPT:</div>
                                    <br>
                                    <div style="text-align:center; font-size:30px; font-weight:bold; font-family:open Sans Helvetica, Arial, sans-serif">{otp}</div>
                                    <br> 
                                    <div style="text-align:center; font-size:20px; font-family:open Sans Helvetica, Arial, sans-serif; padding-left:25px; padding-right:16px">Nếu bạn không thực hiện yêu cầu này, vui lòng bỏ qua email hoặc liên hệ với chúng tôi.</div>
                                    <br>
                                    <div style="text-align:center; font-size:20px; font-family:open Sans Helvetica, Arial, sans-serif; padding-left:25px; padding-right:25px">Chân thành cảm ơn! <br />MyPT team</div>
                                </div>
                            </div>
                        </div>
                    </div>      
                ''', 
                "to" : [email],
                "cc": [],
                "bcc": [],
                "content_fields": {

                },
                "ignore_error": False
            }
        )
        return response_data(otp)
    
    def verify_otp(self, request):
        try:
            data = request.data.copy()
            validate = VerifyOTPValidator(data=data)
            
            if not validate.is_valid():
                return response_data(data=validate.errors, statusCode=4, message="Dữ liệu không hợp lệ!")
            email = data['email']
            otp = data['otp']
            
            otp_in_redis = global_data.redis_service.get_value_by_key(f"otp_{email}")['data']
            
            if str(otp_in_redis) == str(otp):
                return response_data(data="approved")
            
            return response_data(data="otp_incorrect", statusCode=4, message="OTP không chính xác!")
        except Exception as e:
            print(e)
            return response_data(data=str(e), statusCode=4, message="Lỗi hệ thống!")
        
    def resend_otp(self, request):
        return self.sign_up_by_email(request)
