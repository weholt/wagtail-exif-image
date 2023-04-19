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
