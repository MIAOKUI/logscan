import logging
from datetime import datetime
from os import path
from watchdog.events import FileSystemEventHandler
from queue import Queue, Full
from .monitor import Monitor
from .persistance import OffsetPersistance

class WatcherHandler(FileSystemEventHandler):
    def __init__(self, filename, counter, notifier, config, queue_len = 100):
        self.filename = path.abspath(filename)
        self.queue = Queue(queue_len)
        self.monitor = Monitor(self.queue, counter, notifier)
        self.offset_persistance = OffsetPersistance(config)
        self.fd = None
        self.time = datetime.now()
        self.offset = self.offset_persistance.get(filename)
        if path.isfile(self.filename):
            self.fd = open(self.filename)
            self.offset = path.getsize(self.filename)

    def on_created(self, event):
        if event.src_path == self.filename and path.isfile(self.filename):
            self.offset  = 0
            self.fd = open(self.filename, 'r')
            self.fd.seek(self.offset,0)

    def on_deleted(self, event):
        if event.src_path == self.filename:
            self.fd.closed()

    def on_modified(self, event):
        self.fd.seek(self.offset, 0)
        for line in self.fd:
            line = line.rstrip('\n')
            try:
                self.queue.put_nowait(line)
            except Full:
                logging.error('{0} input queue is full!'.format(datetime.now()))
        self.offset = self.fd.tell()
        if (datetime.now() - self.time).seconds > 30:
            self.offset_persistance.put(self.filename, self.offset)
            self.time = datetime.now()

    def on_moved(self, event):
        if path.abspath(event.src_path) == self.filename:
            self.fd.close()
            self.offset = 0

        if path.abspath(event.dest_path) == self.filename:
            self.fd = open(self.filename,'r')
            self.offset = path.getsize(self.fd)

    def start(self):
        self.monitor.start()

    def stop(self):
        self.monitor.stop()
        if self.fd is not None and not self.fd.closed:
            self.fd.close()
        self.offset_persistance.sync()
        self.offset_persistance.close()