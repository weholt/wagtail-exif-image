from django.contrib.auth import get_user_model
from django.db import IntegrityError, models
from django.utils.crypto import get_random_string
from wagtail.images.models import AbstractImage, AbstractRendition, Image

from .utils import get_basic_exif_data, remap_metadata_to_model_fields

User = get_user_model()

BASE_FIELDS = list(Image.admin_form_fields)
BASE_FIELDS.append("story")

EXIF_FIELDS = [
    "title",
    "date_time_original",
    "camera_make",
    "camera_model",
    "lens_model",
    "lens_make",
    "focal_length",
    "shutter_speed",
    "aperture",
    "iso_rating",
    "metering_mode",
    "owner",
    "artist",
    "software",
    "copyright",
    "camera_serial_number",
    "lens_serial_number",
    "lens_specification",
]

IPTC_FIELDS = [
    "by_line",
    "caption",
    "category",
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
    lens_model = models.CharField(max_length=100, null=True, blank=True)
    lens_make = models.CharField(max_length=100, null=True, blank=True)

    owner = models.CharField(max_length=100, null=True, blank=True)
    artist = models.CharField(max_length=100, null=True, blank=True)
    software = models.CharField(max_length=100, null=True, blank=True)
    copyright = models.CharField(max_length=100, null=True, blank=True)
    camera_serial_number = models.CharField(max_length=100, null=True, blank=True)
    lens_serial_number = models.CharField(max_length=100, null=True, blank=True)
    lens_specification = models.CharField(max_length=100, null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude = models.IntegerField(null=True, blank=True)

    admin_form_fields = BASE_FIELDS + EXIF_FIELDS

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.has_processed_metadata:
            from .services import MetadataTransformationService

            with MetadataTransformationService(self.uploaded_by_user) as service:
                default_metadata = service.get_default_metadata(
                    remap_metadata_to_model_fields(
                        get_basic_exif_data(self.file.file.name)
                    )
                )
                service.process_image(self, default_metadata)
                self.save()


class AdvancedIPTCExifImage(BasicExifImage):
    """
    An image model supporting a story and basic EXIF and IPTC fields.
    """

    by_line = models.CharField(max_length=250, null=True, blank=True)
    caption = models.CharField(max_length=250, null=True, blank=True)
    category = models.CharField(max_length=250, null=True, blank=True)
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


def get_key():
    return get_random_string(length=512)


class ImageUploadAccessKey(models.Model):
    """
    A simple user - key mapping to grant access to the upload endpoint.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=512, unique=True, default=get_key)

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


class MetadataDefaultValue(models.Model):
    """
    A key-values mapping for default EXIF and IPTC values.
    This is most useful for IPTC data, making it easy to always
    have your personal info set, copyright information etc.,
    even for photos without any metadata coming in.

    The make and model fields are required to be able to filter
    the assignment of default values to photos, not to clipart etc
    you might upload to your site.

    Note that make, model and target_field are case insensitive.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="metadata_default_values"
    )
    camera_make = models.CharField(max_length=100)
    camera_model = models.CharField(max_length=100)
    target_field = models.CharField(max_length=100)
    target_value = models.CharField(max_length=100)

    class Meta:
        unique_together = ("user", "camera_make", "camera_model", "target_field")

    def save(self, *args, **kwargs):
        self.camera_make = self.camera_make.lower()
        self.camera_model = self.camera_model.lower()
        self.target_field = self.target_field.lower()
        super().save(*args, **kwargs)


class MetadataTransformationValue(models.Model):
    """
    A key-values mapping for default EXIF and IPTC values.
    For instance, Sony's A73 has a model name of ILCE7M3/B which is useless.

    Using the metada transformation you can make a mapping

        source_field: make
        keywords: ILCE7M3/B, ILCE7M3
        target_field: make (or blank)
        target_value: A7III

    Note that source_field, target_field and keywords are case insensitive.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="metadata_transformation_values"
    )
    source_field = models.CharField(max_length=100)
    keywords = models.CharField(
        max_length=200, help_text="List of comma separated values"
    )
    target_value = models.CharField(max_length=100)
    target_field = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = (
            "user",
            "source_field",
            "keywords",
            "target_field",
        )

    def save(self, *args, **kwargs):
        self.source_field = self.source_field.lower()
        self.keywords = self.keywords.lower()
        self.target_field = (
            self.target_field and self.target_field.lower() or self.source_field
        )
        super().save(*args, **kwargs)


class MetadataTransformationSetup(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="metadata_transformation_setup"
    )
    camera_make = models.CharField(max_length=100)
    camera_model = models.CharField(max_length=100)

    convert_categories_to_collections = models.BooleanField(default=False)
    category_divider = models.CharField(max_length=3, default="/")

    convert_camera_make_to_tag = models.BooleanField(default=False)
    convert_camera_model_to_tag = models.BooleanField(default=False)
    convert_lens_make_to_tag = models.BooleanField(default=False)
    convert_lens_model_to_tag = models.BooleanField(default=False)
    copy_caption_abstract_headline_to_title_if_missing = models.BooleanField(
        default=False
    )
    keywords_to_ignore = models.TextField(
        null=True, blank=True, help_text="A list of comma separated keywords to ignore"
    )
    characters_to_trim_from_keywords = models.CharField(max_length=100, default="~")

    class Meta:
        unique_together = ("user", "camera_make", "camera_model")

    def save(self, *args, **kwargs):
        if self.keywords_to_ignore:
            self.keywords_to_ignore = ", ".join(
                [
                    keyword.strip().capitalize()
                    for keyword in self.keywords_to_ignore.split(",")
                ]
            )
        super().save(*args, **kwargs)
