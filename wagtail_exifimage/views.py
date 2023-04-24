from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt

from .forms import get_upload_form
from .models import ImageUploadAccessKey
from .utils import remap_metadata_to_model_fields

UploadForm = get_upload_form()

from .services import MetadataTransformationService


@csrf_exempt
def upload_exif_image(request):
    upload_key = request.POST.get("upload_key")
    if not upload_key:
        return JsonResponse(
            {"succes": False, "reason": "Missing upload key"}, status=401
        )

    acces_key = ImageUploadAccessKey.get_user_by_key(upload_key)
    if not acces_key:
        return JsonResponse(
            {"succes": False, "reason": "User has no upload access"}, status=401
        )

    if not request.FILES:
        return JsonResponse({"succes": False, "reason": "Missing files"}, status=400)

    with MetadataTransformationService(acces_key.user) as service:
        default_metadata = service.get_default_metadata(
            remap_metadata_to_model_fields(request.POST)
        )
        metadata = service.transform_metadata(default_metadata)

        dict = QueryDict(mutable=True)
        dict.update(metadata)
        form = UploadForm(dict, request.FILES)
        if not form.is_valid():
            return JsonResponse(
                {"succes": False, "reason": "Form errors", "errors": form.errors},
                status=400,
            )

        image = form.save()
        metadata["collections"] = request.POST.get("collections").split("/")
        service.process_image(image, metadata)

    return JsonResponse({"succes": True}, status=201)
