from django import forms
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from wagtail.models import Collection

from .models import ExifImage
from .utils import transform_metadata


class UploadedImageForm(forms.ModelForm):
    class Meta:
        model = ExifImage
        fields = [
            "file",
            "title",
            "camera_make",
            "camera_model",
            "date_time_original",
            "aperture",
            "focal_length",
            "shutter_speed",
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
        ]


@csrf_exempt
def upload_exif_image(request):
    if not request.FILES:
        return JsonResponse({"succes": False, "reason": "Missing files"})

    dict = QueryDict(mutable=True)
    dict.update(transform_metadata(request.POST))
    form = UploadedImageForm(dict, request.FILES)
    if not form.is_valid():
        return JsonResponse(
            {"succes": False, "reason": "Form errors", "errors": form.errors}
        )

    image = form.save()
    if image.keywords:
        tags = [s.strip() for s in image.keywords.split(",")]
        for tag in tags:
            image.tags.add(tag)

    collections = request.POST.get("collections").split("/")
    if collections:
        root_coll = Collection.get_first_root_node()
        for collection in collections:
            children = [c for c in root_coll.get_children()]
            if not collection in [c.name for c in children]:
                root_coll = root_coll.add_child(name=collection)
            else:
                root_coll = [c for c in children if c.name == collection][0]

        image.collection = root_coll
    image.save()
    return JsonResponse({"succes": True})
