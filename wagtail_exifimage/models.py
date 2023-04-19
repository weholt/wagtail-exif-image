from django.db import models
from wagtail.images.models import AbstractImage, AbstractRendition, Image

fields = (
    "title",
    "date_time_original",
    "camera_make",
    "camera_model",
    "focal_length",
    "shutter_speed",
    "aperture",
    "iso_rating",
    "metering_mode",
    "by_line",
    "caption",
    "cateogry",
    "city",
    "country_iso_location_code",
    "country_location_name",
    "credit",
    "state",
    "postal_code",
    "country",
    "phone",
    "email",
    "website",
    "address",
    "headline",
    "keywords",
    "title",
    "source",
    "special_instructions",
    "location",
)


class ExifImage(AbstractImage):
    """
    An image model supporting EXIF and IPTC data.
    """

    date_time_original = models.DateTimeField(null=True, blank=True)
    aperture = models.CharField(max_length=10, null=True, blank=True)
    focal_length = models.CharField(max_length=10, null=True, blank=True)
    iso_rating = models.CharField(max_length=10, null=True, blank=True)
    metering_mode = models.CharField(max_length=10, null=True, blank=True)
    shutter_speed = models.CharField(max_length=20, null=True, blank=True)
    camera_make = models.CharField(max_length=100, null=True, blank=True)
    camera_model = models.CharField(max_length=100, null=True, blank=True)
    by_line = models.CharField(max_length=250, null=True, blank=True)
    caption = models.CharField(max_length=250, null=True, blank=True)
    cateogry = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    copyright_notice = models.CharField(max_length=250, null=True, blank=True)
    country_iso_location_code = models.CharField(max_length=100, null=True, blank=True)
    country_location_name = models.CharField(max_length=100, null=True, blank=True)
    credit = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    headline = models.CharField(max_length=100, null=True, blank=True)
    keywords = models.CharField(max_length=250, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=250, null=True, blank=True)
    special_instructions = models.CharField(max_length=250, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)

    admin_form_fields = Image.admin_form_fields + fields


class ExifRendition(AbstractRendition):
    """
    An image rendition supporting EXIF data.
    """

    image = models.ForeignKey(
        ExifImage, on_delete=models.CASCADE, related_name="renditions"
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
