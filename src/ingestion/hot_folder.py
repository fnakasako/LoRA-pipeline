import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .processing import queue_new_file

class IngestionHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")
            queue_new_file(event.src_path)

def start_watching(path: str):
    event_handler = IngestionHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"Watching for new files in: {path}")
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
    
    if __name__ == "__main__":
        # The directory to manually drop files into:
        DROP_DIRECTORY = "PATH"
        start_watching(DROP_DIRECTORY)