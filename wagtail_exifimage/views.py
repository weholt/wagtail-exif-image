from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from wagtail.models import Collection

from .forms import get_upload_form
from .models import ImageUploadAccessKey
from .utils import transform_metadata

UploadForm = get_upload_form()


@csrf_exempt
def upload_exif_image(request):
    if not request.FILES:
        return JsonResponse({"succes": False, "reason": "Missing files"}, status=400)

    upload_key = request.POST.get("upload_key")
    if not upload_key:
        return JsonResponse(
            {"succes": False, "reason": "Missing upload key"}, status=401
        )

    user = ImageUploadAccessKey.get_user_by_key(upload_key)
    if not user:
        return JsonResponse(
            {"succes": False, "reason": "User has no upload access"}, status=401
        )

    dict = QueryDict(mutable=True)
    dict.update(transform_metadata(request.POST))
    form = UploadForm(dict, request.FILES)
    if not form.is_valid():
        return JsonResponse(
            {"succes": False, "reason": "Form errors", "errors": form.errors},
            status=400,
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

    image.has_processed_metadata = True
    image.save()
    return JsonResponse({"succes": True}, status=201)
