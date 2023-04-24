from django import forms
from django.conf import settings

from .models import EXIF_FIELDS, IPTC_FIELDS, AdvancedIPTCExifImage, BasicExifImage


class BasicExifImageUploadForm(forms.ModelForm):
    class Meta:
        model = BasicExifImage
        fields = ["file", "title", "story"] + EXIF_FIELDS


class AdvancedIPTCExifImageUploadForm(forms.ModelForm):
    class Meta:
        model = AdvancedIPTCExifImage
        fields = ["file", "title", "story"] + EXIF_FIELDS + IPTC_FIELDS


def get_upload_form():
    if not hasattr(settings, "WAGTAILIMAGES_IMAGE_MODEL"):
        raise SystemError(
            "You need to set the WAGTAILIMAGES_IMAGE_MODEL in your settings.py"
        )

    return (
        "wagtail_exifimage.BasicExifImage"
        in getattr(settings, "WAGTAILIMAGES_IMAGE_MODEL")
        and BasicExifImageUploadForm
        or AdvancedIPTCExifImageUploadForm
    )
