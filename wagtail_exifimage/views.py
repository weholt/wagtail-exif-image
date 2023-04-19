from django import forms
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from wagtail.models import Collection

from .models import ExifImage


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


def split_and_divide(string_value):
    try:
        v1, v2 = map(float, string_value.split("/"))  #: ['28/5'],
        return v1 / v2
    except:
        return


def transform_metadata(metadata):
    result = {}
    result["date_time_original"] = metadata.get("EXIF DateTimeOriginal", None)

    result["shutter_speed"] = metadata.get("EXIF ExposureTime", "")
    result["aperture"] = split_and_divide(
        metadata.get("EXIF FNumber", "")
    )  # metadata.get("EXIF FNumber"]  #: ['28/5'],
    result["focal_length"] = metadata.get("EXIF FocalLength", "")
    result["iso_rating"] = metadata.get("EXIF ISOSpeedRatings", "")
    result["metering_mode"] = metadata.get("EXIF MeteringMode", "")

    result["camera_make"] = metadata.get("Image Make", "")
    result["camera_model"] = metadata.get("Image Model", "")
    result["by_line"] = metadata.get("by-line", "")
    result["caption"] = metadata.get("caption/abstract", "")
    result["cateogry"] = metadata.get("category", "")
    result["city"] = metadata.get("city", "")
    result["copyright_notice"] = metadata.get("copyright notice", "")
    result["country_iso_location_code"] = metadata.get(
        "country/primary location code", None
    )
    result["country_location_name"] = metadata.get(
        "country/primary location name", None
    )
    result["credit"] = metadata.get("credit", "")
    result["state"] = metadata.get("custom11", "")
    result["postal_code"] = metadata.get("custom12", "")
    result["country"] = metadata.get("custom13", "")
    result["phone"] = metadata.get("custom14", "")
    result["email"] = metadata.get("custom15", "")
    result["website"] = metadata.get("custom16", "")
    result["address"] = metadata.get("custom9", "")
    result["headline"] = metadata.get("headline", "")
    result["title"] = metadata.get("headline", metadata.get("object name", "No title"))
    result["keywords"] = metadata.get("keywords", "")
    result["state"] = metadata.get("province/state", "")
    result["source"] = metadata.get("source", "")
    result["special_instructions"] = metadata.get("special instructions", "")
    result["location"] = metadata.get("sub-location", "")

    final_result = {}
    for key in result:
        if result[key]:
            final_result[key] = result[key]
    return final_result


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
