from os import path
from watchdog.observers import Observer
from watchdog.events.FileSystemEvenHandler import FileSystemEvenHandler

class watcher(FileSystemEvenHandler):
    def __init__(self, filename, matcher):
        self.filename = filename
        self.path = path.abspath(filename)
        self.matcher = matcher
        self.observer = Observer()
        self.fd = None
        self.offset = 0

    def on_created(self,event):
        if path.isfile(self.path):
            self.offset  = path.getsize(self.path)
            self.fd = open(self.path, 'r')
            self.fd.seek(self.offset,0)

    def on_deleted(self,event):
        if event.src == self.path:
            self.fd.closed()

    def on_modified(self, event):
        self.fd.seek(self.offset, 0)
        for line in self.fd:
            self.match(self)

    def on_moved(self, event):


    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.join()