from datetime import datetime

import exifread
from iptcinfo3 import IPTCInfo, c_datasets


def get_basic_exif_data(filename):
    """ """
    # 'EXIF DateTimeOriginal',
    target_tags = [
        "Image Make",
        "Image Model",
        "EXIF ExposureTime",
        "Image Orientation",
        "Image XResolution",
        "Image YResolution",
        "Image ResolutionUnit",
        "EXIF FNumber",
        "EXIF ExposureProgram",
        "EXIF ISOSpeedRatings",
        "EXIF ExifVersion",
        "EXIF ShutterSpeedValue",
        "EXIF ApertureValue",
        "EXIF BrightnessValue",
        "EXIF ExposureBiasValue",
        "EXIF SubjectDistance",
        "EXIF MeteringMode",
        "EXIF LightSource",
        "EXIF Flash",
        "EXIF FocalLength",
        "EXIF ColorSpace",
    ]

    result = {}
    with open(filename, "rb") as fh:
        tags = exifread.process_file(fh)
        for target_tag in target_tags:
            if target_tag in tags:
                result[target_tag] = tags[target_tag].printable

        if "EXIF DateTimeOriginal" in tags:
            try:
                result["EXIF DateTimeOriginal"] = datetime.strptime(
                    str(tags["EXIF DateTimeOriginal"]), "%Y:%m:%d %H:%M:%S"
                )
            except ValueError:
                print(
                    "error parsing EXIF DateTimeOriginal: %s -> %s"
                    % (filename, str(tags["EXIF DateTimeOriginal"]))
                )

        info = IPTCInfo(filename)
        if info.__dict__ == "":
            return result

        for k, v in info.__dict__.items():
            if k == "_data":
                for key, value in v.items():
                    if key in c_datasets:
                        field = c_datasets[key]
                        try:
                            v = value.decode("utf-8")
                        except:
                            if isinstance(value, list):
                                v = ", ".join([p.decode("utf-8") for p in value])
                            else:
                                v = str(value)
                        result[field] = v
    return result


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
