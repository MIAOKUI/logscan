import shelve
import threading


class Counter:
    def __init__(self, db_path):
        self.db_path = db_path
        self.db = shelve.open(db_path)
        self.lock = threading.Lock()
        self.is_stop = False

    def inc(self, name):
        with self.lock:
            self.db[name] += 1

    def get(self, name):
        with self.lock:
            return self.db[name]

    def clean(self, name):
        with self.lock:
            if name in self.db.keys():
                self.db[name] = 0

    def stop(self):
        with self.lock:
            if not self.is_stop:
                self.db.sync()
                self.db.close()
