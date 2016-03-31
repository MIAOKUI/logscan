from os import path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from count import Counter
from match import Matcher

class Watcher(FileSystemEventHandler):
    def __init__(self, filename, db_path, exprs, exprs_name):
        self.filename = path.abspath(filename)
        self.matcher = Matcher(exprs)
        self.exprs_name = exprs_name
        self.counter = Counter(db_path)
        self.observer = Observer()
        self.fd = None
        self.offset = 0
        if path.isfile(self.filename):
            self.fd = open(self.filename)
            self.offset = path.getsize(self.filename)

    def on_created(self,event):
        print('file appear')
        if path.isfile(self.filename):
            self.offset  = path.getsize(self.filename)
            self.fd = open(self.filename, 'r')
            self.fd.seek(self.offset,0)

    def on_deleted(self,event):
        if event.src_path == self.filename:
            self.fd.closed()

    def on_modified(self, event):
        self.fd.seek(self.offset, 0)
        for line in self.fd:
            if self.matcher(line):
                self.counter.inc(self.exprs_name)
        self.offset = self.fd.tell()

    def on_moved(self, event):
        if event.src_path == self.filename:
            self.fd.close()

        if event.dest_path == self.filename:
            self.offset = 0
            self.fd = open(self.filename,'r')
            self.fd.seek(self.offset, 0)
            for line in self.fd:
                self.matcher(line)
            self.offset = self.fd.tell()

    def start(self):
        self.observer.schedule(self, path.dirname(self.filename), recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.join()


if __name__  == '__main__':
    w = Watcher('test1.txt', matcher)
    w.start()
    w.stop()