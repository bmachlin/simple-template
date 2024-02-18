import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
from TemplateLoader import TemplateLoader, fillTemplate

last_trigger_time = time.time()
templates = {}

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # use global variable to avoid multiple triggers
        global last_trigger_time
        current_time = time.time()
        if event.src_path.find('~') != -1 or (current_time - last_trigger_time) < 1:
            return
        
        last_trigger_time = current_time
        if event.is_directory:
            return
        elif event.event_type == "modified":
            processHTMLFile(event.src_path)
    

if __name__ == "__main__":
    print(sys.argv)
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    tl = TemplateLoader(path + "/templates")
    templates = tl.getAll()
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
