import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
# from TemplateLoader import TemplateLoader, fillTemplate

# templates = {}

class SimpleTemplateHandler(FileSystemEventHandler):
    def __init__(self):
        super(SimpleTemplateHandler, self).__init__()
        self.last_trigger_time = time.time()
        
    def on_any_event(self, event):
        current_time = time.time()
        if event.is_directory or (current_time - self.last_trigger_time) < 1:
            return
        self.last_trigger_time = current_time
        print("\n\n", event.event_type, "event for", event.src_path)
        
        # processHTMLFile(event.src_path)
    

if __name__ == "__main__":
    config_path = "./tml_config.json" # default config file to use
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    
    
    event_handler = SimpleTemplateHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
