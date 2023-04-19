import os
import sys
import time

import djclick as click
import requests
import watchdog.events
import watchdog.observers
from django.conf import settings

from wagtail_exifimage.utils import get_basic_exif_data


def upload_file(url, filename, collections):
    if not os.path.exists(filename):
        return

    try:
        metadata = get_basic_exif_data(filename)
        metadata["collections"] = collections
        try:
            with open(filename, "rb") as f:
                r = requests.post(url, data=metadata, files={"file": f})
            print("Uploaded %s" % filename)
        except ConnectionError:
            print("Error connecting to %s" % url)
        except PermissionError:
            print("Permission error reading %s" % filename)
    except Exception as ex:
        print("Error processing %s: %s" % (filename, ex))
    except KeyboardInterrupt:
        sys.exit(0)


class Handler(watchdog.events.PatternMatchingEventHandler):
    """
    The handler looking for new images.
    """

    def __init__(self, source_path: str):
        self.uploaded_files = []
        self.source_path = source_path
        # Set the patterns for PatternMatchingEventHandler
        watchdog.events.PatternMatchingEventHandler.__init__(
            self,
            patterns=["*.jpg", "*.png", "*.webp"],
            ignore_directories=True,
            case_sensitive=False,
        )

    def on_created(self, event):
        init_size = -1
        while True:
            current_size = os.path.getsize(event.src_path)
            if current_size == init_size:
                break
            else:
                init_size = os.path.getsize(event.src_path)
                time.sleep(2)

        if not event.src_path in self.uploaded_files:
            p, _ = os.path.split(event.src_path)
            collections = p[len(self.source_path) :].replace(os.sep, "/")
            if not collections and hasattr(
                settings, "EXIF_IMAGE_UPLOAD_DEFAULT_COLLECTION"
            ):
                collections = settings.EXIF_IMAGE_UPLOAD_DEFAULT_COLLECTION
            upload_file(settings.EXIF_IMAGE_UPLOAD_URL, event.src_path, collections)
            self.uploaded_files.append(event.src_path)


@click.command()
def start_image_watcher():
    src_path = settings.EXIF_IMAGE_WATCHED_FOLDER
    if not src_path[:-1] == os.sep:
        src_path += os.sep
    print("Watching %s for new files ..." % src_path)
    event_handler = Handler(src_path)
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
