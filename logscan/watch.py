import logging
from os import path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from queue import Queue, Full
from .monitor import Monitor

class Watcher(FileSystemEventHandler):
    def __init__(self, filename, counter, notifier, offset_db, queue_len = 100):
        self.counter = counter
        self.queue = Queue(1000)
        self.monitor = Monitor()
        self.fd = None
        self.offset = 0

        # If file monitored file exist, open it and moving the cursor to the bottom
        if path.isfile(self.filename):
            self.fd = open(self.filename)
            self.offset = path.getsize(self.filename)

    def on_created(self, event):
        # if the created file is our target file
        # then open the file and move the cursor to the beginning
        if event.src_path == self.filename and path.isfile(self.filename):
            self.offset  = 0
            self.fd = open(self.filename, 'r')
            self.fd.seek(self.offset,0)

    def on_deleted(self, event):
        # if the deleted file is our monitored file
        # close the file
        if event.src_path == self.filename:
            self.fd.closed()

    def on_modified(self, event):
        # if the modified file is our monitored file
        # move the cursor to the current offset and read line into queue
        self.fd.seek(self.offset, 0)
        for line in self.fd:
            try:
                self.queue.put_nowait(line)
            except Full:
                logging.error('input queue is full!')
        self.offset = self.fd.tell()

    def on_moved(self, event):
        # if our monitored file was moved to other place
        # then close the file
        if event.src_path == self.filename:
            self.fd.close()
            self.offset = 0
        # if our monitored file was moved into observed directory
        # Read from beginning and put lines input queue
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