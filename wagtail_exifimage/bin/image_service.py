import logging
import os
import sys
import time

import requests
import watchdog.events
import watchdog.observers
from dotenv import load_dotenv

from wagtail_exifimage.utils import get_basic_exif_data

load_dotenv()

EXIF_IMAGE_WATCHED_FOLDER = os.getenv("EXIF_IMAGE_WATCHED_FOLDER")
EXIF_IMAGE_UPLOAD_URL = os.getenv("EXIF_IMAGE_UPLOAD_URL")
EXIF_IMAGE_UPLOAD_DEFAULT_COLLECTION = os.getenv("EXIF_IMAGE_UPLOAD_DEFAULT_COLLECTION")
EXIF_IMAGE_UPLOAD_KEY = os.getenv("EXIF_IMAGE_UPLOAD_KEY")

logging.basicConfig(filename="image_service.log", encoding="utf-8", level=logging.DEBUG)


def upload_file(upload_key, url, filename, collections):
    """
    Will try to upload an image and its metadata to a given url.
    """
    if not os.path.exists(filename):
        return

    try:
        metadata = get_basic_exif_data(filename)
        metadata["collections"] = collections
        metadata["upload_key"] = upload_key
        try:
            with open(filename, "rb") as f:
                r = requests.post(url, data=metadata, files={"file": f}, timeout=10)
            logging.info(f"Uploaded {filename}. Result: {r.content}")
        except ConnectionError:
            logging.warning(f"Error connecting to {url}")
        except PermissionError:
            logging.warning(f"Permission error reading {filename}")
    except Exception as ex:
        logging.warning(f"Error processing {filename}: {ex}")
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

        if event.src_path not in self.uploaded_files:
            p, _ = os.path.split(event.src_path)
            collections = p[len(self.source_path) :].replace(os.sep, "/")
            if not collections and EXIF_IMAGE_UPLOAD_DEFAULT_COLLECTION:
                collections = EXIF_IMAGE_UPLOAD_DEFAULT_COLLECTION

            upload_file(
                EXIF_IMAGE_UPLOAD_KEY,
                EXIF_IMAGE_UPLOAD_URL,
                event.src_path,
                collections,
            )
            self.uploaded_files.append(event.src_path)


def main():
    src_path = EXIF_IMAGE_WATCHED_FOLDER
    if not src_path[:-1] == os.sep:
        src_path += os.sep

    print("=" * 80)
    print(f"Watching {src_path} for new files ...")
    print("\n - Logging to image_service.log\n")
    print("=" * 80)

    if not os.path.exists(src_path):
        logging.error(f"Path does not exist: {src_path}")
        sys.exit(1)

    logging.info(f"Watching {src_path} for new files ...")
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


if __name__ == "__main__":
    main()
