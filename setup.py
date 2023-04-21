from setuptools import find_packages, setup

setup(
    name="wagtail_exifimage",
    version="0.1",
    description="A simple reusable django / wagtail app for providing metadata like Exif and Iptc in images",
    url="https://github.com/weholt/wagtail_exifimage",
    author="Thomas Weholt",
    author_email="thomas@weholt.org",
    license="MIT",
    install_requires=[
        "watchdog",
        "exifread",
        "requests",
        "iptcinfo3",
        "django",
        "wagtail",
        "django-click",
        "python-dotenv",
    ],
    packages=find_packages(),  # ["wagtail_exifimage"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "image_service = wagtail_exifimage.bin.image_service:main",
        ]
    },
    zip_safe=False,
)
