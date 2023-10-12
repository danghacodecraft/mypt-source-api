from django.urls import path
from .http.views.health_view import *
from .http.views.upload_file_view import *
from .http.views.show_file_view import *

urlpatterns = [
    path('health', HealthView.as_view({'get': 'health'})),
    path('upload-file', UploadFile.as_view({'post': 'upload_file'})),
    path('view-file', ShowFile.as_view({'get': 'show_file'})),
    path('view-file-auth', ShowFile.as_view({'get': 'show_file_auth'})),
    path('view-image-iqc', ShowFile.as_view({'get': 'show_image_iqc'})),

    path('upload-file-private', UploadFile.as_view({'post': 'upload_file_private'})),
]


