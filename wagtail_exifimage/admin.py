from django.contrib import admin

from .models import (
    AdvancedIPTCExifImage,
    BasicExifImage,
    ImageUploadAccessKey,
    MetadataDefaultValue,
    MetadataTransformationSetup,
    MetadataTransformationValue,
)


@admin.register(ImageUploadAccessKey)
class ImageUploadAccessKeyAdmin(admin.ModelAdmin):
    list_display = ["user", "key"]


@admin.register(BasicExifImage)
class BasicExifImageAdmin(admin.ModelAdmin):
    pass


@admin.register(AdvancedIPTCExifImage)
class AdvancedIPTCExifImageAdmin(admin.ModelAdmin):
    pass


@admin.register(MetadataDefaultValue)
class MetadataDefaultValueAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "camera_make",
        "camera_model",
        "target_field",
        "target_value",
    ]
    readonly_fields = ["user"]

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(MetadataTransformationValue)
class MetadataTransformationValueAdmin(admin.ModelAdmin):
    list_display = ["user", "source_field", "keywords", "target_value", "target_field"]
    readonly_fields = ["user"]

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(MetadataTransformationSetup)
class MetadataTransformationSetupAdmin(admin.ModelAdmin):
    list_display = ["user", "camera_make", "camera_model"]
    readonly_fields = ["user"]

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)
