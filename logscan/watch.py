import logging
from os import path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from queue import Queue, Full
from .check import CheckerChain

class Watcher(FileSystemEventHandler):
    def __init__(self, filename, counter):
        self.filename = path.abspath(filename)
        self.observer = Observer()
        self.counter = counter
        self.queue = Queue(1000)
        self.checker_chain = CheckerChain(self.queue, self.counter)
        self.fd = None
        self.offset = 0
        if path.isfile(self.filename):
            self.fd = open(self.filename)
            self.offset = path.getsize(self.filename)

    def on_created(self,event):
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
            try:
                self.queue.put_nowait(line)
            except Full:
                logging.error('input queue is full!')
        self.offset = self.fd.tell()

    def on_moved(self, event):
        if event.src_path == self.filename:
            self.fd.close()

        if event.dest_path == self.filename:
            self.offset = 0
            self.fd = open(self.filename,'r')
            self.fd.seek(self.offset, 0)
            for line in self.fd:
                try:
                    self.queue.put_nowait(line)
                except Full:
                    logging.error('input queue is full')
            self.offset = self.fd.tell()

    def start(self):
        self.checker_chain.start()
        self.observer.schedule(self, path.dirname(self.filename), recursive=False)
        self.observer.start()
        self.observer.join()

    def stop(self):
        self.checker_chain.stop()
        self.observer.stop()
        if self.fd is not None and not self.fd.closed:
            self.fd.close()


if __name__  == '__main__':
    w = Watcher('test1.txt', matcher)
    w.start()
    w.stop()