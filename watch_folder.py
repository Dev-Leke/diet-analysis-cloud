"""
watch_folder.py
Task 3 - Optional: simulate an event-driven (serverless) trigger.

Real Azure Functions fire AUTOMATICALLY when a blob is uploaded. Azurite can't,
so we watch a local 'dropzone' folder. When a CSV is dropped in, this:
  1. Detects the "event" (a new file appears)
  2. Uploads that file to Azurite Blob Storage
  3. Invokes the serverless function to process it -> results.json

Usage:
  Terminal 1:  python watch_folder.py        (starts watching, stays running)
  Terminal 2:  cp All_Diets.csv dropzone/     (triggers the chain)
  Stop with Ctrl+C in Terminal 1.
"""

import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from azure.storage.blob import BlobServiceClient

# Reuse config + processing logic from the serverless function.
# Because that file guards its run with `if __name__ == "__main__"`, importing
# it gives us the function WITHOUT running it now.
from serverless_function import (
    process_nutritional_data,
    CONNECTION_STRING,
    CONTAINER_NAME,
    BLOB_NAME,
)

WATCH_DIR = "dropzone"


def upload_to_blob(local_path):
    """Upload a dropped file into Azurite under the blob name the function reads."""
    service = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container = service.get_container_client(CONTAINER_NAME)
    if not container.exists():
        container.create_container()
    with open(local_path, "rb") as data:
        container.upload_blob(name=BLOB_NAME, data=data, overwrite=True)
    print(f"  Uploaded {local_path} -> {CONTAINER_NAME}/{BLOB_NAME}")


class CsvDropHandler(FileSystemEventHandler):
    """Reacts whenever a new file is created in the watched folder."""
    def on_created(self, event):
        # Ignore subfolders; react only to .csv files.
        if event.is_directory or not event.src_path.lower().endswith(".csv"):
            return
        print(f"\n[EVENT] New file detected: {event.src_path}")
        time.sleep(1)  # let the file finish copying before we read it
        upload_to_blob(event.src_path)
        print("  Invoking serverless function...")
        process_nutritional_data()
        print("  Done. Waiting for the next file...\n")


def main():
    os.makedirs(WATCH_DIR, exist_ok=True)
    observer = Observer()
    observer.schedule(CsvDropHandler(), WATCH_DIR, recursive=False)
    observer.start()
    print(f"Watching '{WATCH_DIR}/' for new CSV files. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped watching.")
    observer.join()


if __name__ == "__main__":
    main()
