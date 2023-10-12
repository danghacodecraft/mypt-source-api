import base64
import os
import datetime
import json
import copy
from django.conf import settings
from ...core.helpers.schedule import CronBase
from ...core.helpers.response import response_data
from ...core.helpers.capture_image_via_url import capturer_as_base64
from ...core.helpers.string_to_int_representation import string_to_int_representation
from ..serializers.email_template_serializer import EmailTemplateSerializer
from ..serializers.email_schedule_information_serializer import EmailScheduleInformationSerializer
from ..validation.email_service_validator import EmailServiceValidation,\
                                                EmailContentFieldValidator, EmailWithTemplateServiceValidation,\
                                                ImageAttachValidator
from ..models.email_template import EmailTemplate
from ..models.email_schedule_information import EmailScheduleInformation
from rest_framework.viewsets import ViewSet
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
from django.db import close_old_connections, connection

IMAGES_BASE64 = {}
mypt_schedule = CronBase()
mypt_schedule.start()
class EmailReportViewSet(ViewSet):
    def email_initial(self, request=None):
        print("------> email_initial")
        try:
            queryset = EmailScheduleInformation.objects.filter(is_done=False)
            
            if queryset:
                serializers = EmailScheduleInformationSerializer(queryset, many=True)
                for s in serializers.data:
                    
                    data_str = s['input_data']
                    data_str = data_str.replace("'", '"')
                    data_str = data_str.replace("False", "false")
                    data_str = data_str.replace("True", "true")
                    data = json.loads(data_str)
                    data['schedule_id'] = s['name']
            
                    self.add_report_email_schedule(data)
            return response_data()
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message=str(e))
    
    def send_one_mail(self, request):
        try:
            return self.send_email(request.data)
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message=str(e))
    
    def send_with_template(self, request):
        try:
            data = request.data.copy()
            validate = EmailWithTemplateServiceValidation(data=data)
            
            if not validate.is_valid():
                return response_data(statusCode=4, message=validate.errors)
            
            data = validate.data
            
            template = data['template']
            subject = data['subject']
            to = data['to']
            cc = data['cc']
            bcc = data['bcc']
            content_fields = data['content_fields']
            
            mail = EmailMultiAlternatives(
                    subject=subject,
                    # body=html,
                    from_email=settings.EMAIL_HOST_USER,
                    to=to,
                    cc=cc,
                    bcc=bcc,
                    headers={'Message-ID': 'thuannt29-pnc-pdx'}
            )
            mail.content_subtype = 'html'
            mail.mixed_subtype = 'related'
            
            content_fields["today"] = datetime.datetime.now().date().strftime("%d-%m-%Y")
            t = Template(template)
            c = Context(content_fields)
            html = t.render(c)
            
            mail.body = html
            sent = mail.send()
            if not sent:
                print("Send Email Failure")
                return response_data(statusCode=4, message="Send Email Failure")
            print("sent...")
            return response_data()
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message=str(e))
    
    def send_email(self, request_data):
        print("sending...")
        try:
            data = request_data
            validate = EmailServiceValidation(data=data)
            
            if not validate.is_valid():
                print(validate.errors)
                return response_data(statusCode=4, message=validate.errors)
            
            data = validate.data
            print(f"---> check db connection: {connection.ensure_connection()}")
            template = EmailTemplate.objects.filter(template_name=data['template_name'], is_deleted=False)
            
            if not template:    
                print("template not found")
                return response_data(statusCode=4, message="template not found")
            
            template_serializer = EmailTemplateSerializer(template, many=True).data
            template_data = json.loads(json.dumps(template_serializer))[0]
            template_fields = template_data['field_require'].split(';')
      
            content_fields_validate = EmailContentFieldValidator(data=data['content_fields'])
            
            if not content_fields_validate.is_valid():
                print(content_fields_validate.errors)
                return response_data(statusCode=4, message=content_fields_validate.errors)
            
            for template_field in template_fields:
                if data['content_fields'].get(template_field, None) is None:
                    print(f"{template_field} in content_fields is require")
                    return response_data(statusCode=4, message=f"{template_field} in content_fields is require") 
            
            images = data['content_fields'].pop("images", [])
            
            try:
                mail = EmailMultiAlternatives(
                    subject=data['subject'],
                    # body=html,
                    from_email=settings.EMAIL_HOST_USER,
                    to=data['to'],
                    cc=data['cc'],
                    bcc=data['bcc'],
                    headers={'Message-ID': 'thuannt29-pnc-pdx'}
                )
                mail.content_subtype = 'html'
                mail.mixed_subtype = 'related'

                for image in images:
                    image_attach_validate = ImageAttachValidator(data=image)
                    
                    if not image_attach_validate.is_valid():
                        print(image_attach_validate.errors)
                        if data['ignore_error']:
                            continue
                        else:
                            return response_data(statusCode=4, message=image_attach_validate.errors) 
                    
                    if "LINK" == image['attach_type']:
                        data['content_fields'][image['name_in_html']] = image['image_url']
                    elif "CID" == image['attach_type']:
                        image_id = str(string_to_int_representation(image['image_url']))
                        now_str = datetime.datetime.now().date().strftime("%d_%m_%Y")
                        
                        if len(image_id) > 20:
                            image_id = f'{image_id[:10]}{image_id[-10:]}'
                            
                        image_id = f"{image_id}_{now_str}"
                            
                        if image_id in IMAGES_BASE64:
                            pass
                            image_base64 = IMAGES_BASE64[image_id]
                            image_data = base64.b64decode(image_base64)
                            image_attach = MIMEImage(image_data)
                            image_name = image['name_in_html']
                            cid_name = f'<{image_name}>'
                            image_attach.add_header('Content-ID', cid_name)
                            mail.attach(image_attach)

                        else:
                            print("no report image")
                            if data['ignore_error']:
                                continue
                            else:
                                return response_data(data="NO_REPORT_IMAGE", statusCode=4, message="no report image")
                    elif "BASE64" == image['attach_type']:
                        image_id = str(string_to_int_representation(image['image_url']))
                        
                        if len(image_id) > 20:
                            image_id = f'{image_id[:10]}{image_id[-10:]}'

                        if image_id not in IMAGES_BASE64:
                            print("no report image")
                            if data['ignore_error']:
                                continue
                            else:
                                return response_data(data="NO_REPORT_IMAGE", statusCode=4, message="no report image")
                        
                        data['content_fields'][image['name_in_html']] = IMAGES_BASE64.get(image_id, "")
                
                data['content_fields']["today"] = datetime.datetime.now().date().strftime("%d-%m-%Y")
                template_html = template_data['html']
                t = Template(template_html)
                c = Context(data['content_fields'])
                html = t.render(c)
                
                mail.body = html

                sent = mail.send()
                # sent = True
                
                if not sent:
                    print("Send Email Failure")
                    return response_data(statusCode=4, message="Send Email Failure")
                print("sent...")
                return response_data()
            except Exception as e:
                print(e)
                return response_data(statusCode=4, message="Email Service Error")
        except Exception as e:
            print(f"---> {e}")
            close_old_connections()
            return response_data(statusCode=4, message="Server Error")

    def add_report_email_schedule(self, data):
        schedule_id = data.get('schedule_id', datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S"))
        
        email_stt = mypt_schedule.add_task(callback=self.send_report_email_handler,\
            cron=data["send_email_schedule"],\
            task_id=self.send_report_email_handler.__name__+"_"+schedule_id,
            request_data=data
        )
            
        capture_stt = mypt_schedule.add_task(callback=self.capture_report_image_handler,\
            cron=data["capture_report_schedule"],\
            task_id=self.capture_report_image_handler.__name__+"_"+schedule_id,
            request_data=data
        )
        
        return email_stt, capture_stt
    
    def send_report_email(self, request):
        try:              
            data = request.data
            if "send_email_schedule" not in data: 
                return response_data(statusCode=4, message="'send_email_schedule' is required")
            if "capture_report_schedule" not in data:
                return response_data(statusCode=4, message="'capture_report_schedule' is required")
            
            schedule_id = self.create_schedule_id(data) 
            data['schedule_id'] = schedule_id
            
            email_stt, capture_stt = self.add_report_email_schedule(data)
            data_to_save = copy.copy(data)
            data_to_save.pop("schedule_id", None)
            
            if email_stt[0] and capture_stt[0]:
                schedule_data = {
                    "name": schedule_id,
                    "input_data": str(data_to_save)
                }
                
                schedule_serializer = EmailScheduleInformationSerializer(data=schedule_data)
                
                if schedule_serializer.is_valid():
                    schedule_serializer.save()
                    return response_data()
                print(schedule_serializer.errors)
                return response_data(data=schedule_serializer.errors, message="Success Initialization But Not Saved")

            self.clear_schedule(self.capture_report_image_handler.__name__+"_"+schedule_id)
            self.clear_schedule(self.send_report_email_handler.__name__+"_"+schedule_id)
            return response_data({"email": email_stt, "capture": capture_stt}, statusCode=4)
        
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")
   
    def capture_one_image(self, request):
        try:
            return self.capture_image_report(request.data)
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message=str(e))
        
    def capture_image_report(self, request_data):        
        try:   
            print("capturing...")    
            data = request_data
            image_data = data['image']
            if "image_url" not in image_data:
                return response_data(statusCode=4, message="'image_url' is required")
            
            image_url = image_data['image_url']    
            size = image_data.get('size', [0, 0]) 
            is_full_page = image_data.get('full_page', False) or (size is [0, 0])
            image_id = str(string_to_int_representation(image_url))
            
            if len(image_id) > 20:
                image_id = f'{image_id[:10]}{image_id[-10:]}'
            captured, capture_message = capturer_as_base64(image_url, size)

            if captured:
                now_str = datetime.datetime.now().date().strftime("%d_%m_%Y")
                IMAGES_BASE64[f"{image_id}_{now_str}"] = captured
                print("captured...")   
                return response_data(message=capture_message)
            else:
                return response_data(data="CAPTURE_FAILURE", statusCode=4, message=capture_message)
        except Exception as e:
            print(e)
            return response_data(data="CAPTURE_FAILURE", statusCode=4, message=str(e))
    
    def capture_image_report_review(self, request):        
        try:   
            print("capturing...")    
            image_data = request.data['image']
            if "image_url" not in image_data:
                return response_data(statusCode=4, message="'image_url' is required")
            
            image_url = image_data['image_url']    
            size = image_data.get('size', [0, 0]) 
            is_full_page = image_data.get('full_page', False) or (size is [0, 0])
            image_id = str(string_to_int_representation(image_url))
            
            if len(image_id) > 20:
                image_id = f'{image_id[:10]}{image_id[-10:]}'
            captured, capture_message = capturer_as_base64(image_url, size)

            if captured:
                print("captured...")   
                return response_data(data=IMAGES_BASE64, message=captured)
            else:
                return response_data(data="CAPTURE_FAILURE", statusCode=4, message=capture_message)
        except Exception as e:
            print(e)
            return response_data(data="CAPTURE_FAILURE", statusCode=4, message=str(e))
    
    def send_report_email_handler(self, request_data):
        mypt_schedule.clear_task(f"re_send_{request_data['schedule_id']}")

        email_response = self.send_email(request_data)
        
        if 1 != email_response.data['statusCode']:
            def re_send():
                print("re-send")
                email_response = self.send_email(request_data)
                
                if 1 == email_response.data['statusCode']:
                    mypt_schedule.clear_task(f"re_send_{request_data['schedule_id']}")
            
            cron = "*/3 * * * * 50"
            mypt_schedule.add_task(callback=re_send,\
                cron=cron,\
                task_id=f"re_send_{request_data['schedule_id']}"
            )     
            
    def capture_report_image_handler(self, request_data):
        mypt_schedule.clear_task(f"re_capture_{request_data['schedule_id']}")
        
        capture_response = self.capture_image_report(request_data)

        if 1 != capture_response.data['statusCode']:
            def re_capture():
                capture_res = self.capture_image_report(request_data)
                
                if 1 == capture_res.data['statusCode']:
                    mypt_schedule.clear_task(f"re_capture_{request_data['schedule_id']}")
                    
            cron = "*/2 * * * * 5"
            mypt_schedule.add_task(callback=re_capture, \
                cron=cron, \
                task_id=f"re_capture_{request_data['schedule_id']}"
            )

    def create_schedule_id(self, data):
        name = str(string_to_int_representation(str(data)))
        
        if len(name) > 20:
            name = f"{name[:10]}{name[-10:]}"
            
        return name

    def clear_all_schedules(self, request):
        try:
            IMAGES_BASE64.clear()
            mypt_schedule.clear_all()
            return response_data()
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message=str(e))
    
    def clear_schedule(self, request):
        try:
            data = request.data
            if "schedule_id" not in data:
                return response_data(statusCode=4, message="'schedule_id' is required")
            
            mypt_schedule.clear_task(data['schedule_id'])
            return response_data()
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message=str(e))
