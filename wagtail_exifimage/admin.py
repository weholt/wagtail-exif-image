from django.contrib import admin

from .models import AdvancedIPTCExifImage, BasicExifImage, ImageUploadAccessKey


@admin.register(ImageUploadAccessKey)
class ImageUploadAccessKeyAdmin(admin.ModelAdmin):
    list_display = ["user", "key"]


@admin.register(BasicExifImage)
class BasicExifImageAdmin(admin.ModelAdmin):
    pass


@admin.register(AdvancedIPTCExifImage)
class AdvancedIPTCExifImageAdmin(admin.ModelAdmin):
    pass
