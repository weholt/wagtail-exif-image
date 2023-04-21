from django.contrib.auth import get_user_model
from django.db import IntegrityError, models
from django.utils.crypto import get_random_string
from wagtail.images.models import AbstractImage, AbstractRendition, Image

from .utils import get_basic_exif_data, transform_metadata

User = get_user_model()
BASE_FIELDS = list(Image.admin_form_fields)
BASE_FIELDS.append("story")

EXIF_FIELDS = [
    "title",
    "date_time_original",
    "camera_make",
    "camera_model",
    "focal_length",
    "shutter_speed",
    "aperture",
    "iso_rating",
    "metering_mode",
]

IPTC_FIELDS = [
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
]


class BasicExifImage(AbstractImage):
    """
    An image model supporting a story and basic EXIF fields.
    """

    story = models.TextField(null=True, blank=True)
    has_processed_metadata = models.BooleanField(default=False)

    date_time_original = models.DateTimeField(null=True, blank=True)
    aperture = models.CharField(max_length=10, null=True, blank=True)
    focal_length = models.CharField(max_length=10, null=True, blank=True)
    iso_rating = models.CharField(max_length=10, null=True, blank=True)
    metering_mode = models.CharField(max_length=10, null=True, blank=True)
    shutter_speed = models.CharField(max_length=20, null=True, blank=True)
    camera_make = models.CharField(max_length=100, null=True, blank=True)
    camera_model = models.CharField(max_length=100, null=True, blank=True)

    admin_form_fields = BASE_FIELDS + EXIF_FIELDS

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.has_processed_metadata:
            metadata = transform_metadata(get_basic_exif_data(self.file.file.name))
            for attr, value in metadata.items():
                setattr(self, attr, value)
                self.has_processed_metadata = True

            if metadata.get("keywords"):
                tags = [s.strip() for s in metadata.get("keywords").split(",")]
                for tag in tags:
                    self.tags.add(tag)

            self.save()  # update_fields=metadata.keys())


class AdvancedIPTCExifImage(BasicExifImage):
    """
    An image model supporting a story and basic EXIF and IPTC fields.
    """

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
    state = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=250, null=True, blank=True)
    special_instructions = models.CharField(max_length=250, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)

    admin_form_fields = BASE_FIELDS + EXIF_FIELDS + IPTC_FIELDS


class BasicExifRendition(AbstractRendition):
    """
    An image rendition supporting EXIF data.
    """

    image = models.ForeignKey(
        BasicExifImage, on_delete=models.CASCADE, related_name="renditions"
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)


class AdvancedIPTCExifRendition(AbstractRendition):
    """
    An image rendition supporting EXIF and IPTC data.
    """

    image = models.ForeignKey(
        AdvancedIPTCExifImage,
        on_delete=models.CASCADE,
        related_name="advanced_renditions",
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)


class ImageUploadAccessKey(models.Model):
    """
    A simple user - key mapping to grant access to the upload endpoint.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    key = models.CharField(
        max_length=512, unique=True, default=get_random_string(length=512)
    )

    @classmethod
    def get_key(cls, username: str) -> str:
        while True:
            try:
                obj, _ = cls.objects.get_or_create(
                    user=User.objects.get(username=username),
                    defaults={"key": get_random_string(length=512)},
                )
                return obj.key
            except IntegrityError:
                pass

    @classmethod
    def get_user_by_key(cls, key: str) -> User:
        return cls.objects.filter(key=key).first()
