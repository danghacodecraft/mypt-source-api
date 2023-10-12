from rest_framework.viewsets import ViewSet
from core.helpers.response import response_data
from ..models.email_template import EmailTemplate
from ..serializers.email_template_serializer import EmailTemplateSerializer

class EmailTemplateViewSet(ViewSet):
    def add_template(self, request):
        try:
            data = request.data
            serializer = EmailTemplateSerializer(data=data)
            
            if serializer.is_valid():
                serializer.save()
                return response_data()
            return response_data(statusCode=4, message=serializer.errors)
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")
    
    def remove_template(self, request):
        try:
            data = request.data
            
            if not "template_name" in data:
                return response_data(statusCode=4, message="'template_name' is required") 
            
            template_name = data['template_name']
            
            try:
                tpl = EmailTemplate.objects.filter(template_name=template_name, is_deleted=False).first()
                tpl.is_deleted = True
                tpl.save()
                return response_data()
            except Exception as e:
                print(e)
                return response_data(statusCode=4, message="Template not found")    
             
        except Exception as e:
            print(e)
            return response_data(statusCode=4, message="Server Error")