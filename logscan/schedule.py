from .watch import WatcherHandler
from .count import Counter
import threading
from os import path

class Scheduler:
    def __init__(self, db_p):
        self.counter = Counter(db_path)
        self.watcher = {}
        self.threads = {}

    def add_watcher(self, filename):
        watcher = Watcher(filename, self.counter)
        self._add_watcher(watcher)

    def _add_watcher(self, watcher):
        if watcher.filename not in self.watcher.keys():
            t = threading.Thread(target = watcher.start, name = watcher.name)
            t.daemon = True
            t.start()
            t.join()
            self.threads[watcher.filename] = t

    def remove_watcher(self, filename):
        key_name = path.abspath(filename)
        if key_name in self.watcher.keys():
            self.watcher[key_name].stop()
            self.threads[key_name].join()
            self.watcher.pop(key_name)
            self.threads.pop(key_name)

    def stop(self):
        for w in self.watcher.value()[:]:
            w.stop()
        self.counter.stop()
