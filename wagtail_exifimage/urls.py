from django.urls import include, path

from . import views

urlpatterns = [
    path("exif-image/upload/", views.upload_exif_image),
]
