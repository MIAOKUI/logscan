from match import Matcher
from watch import Watcher
import threading
from os import path

class Scheduler:
    def __init__(self):
        self.matcher = None
        self.watcher = {}
        self.threads = {}

    def add_watcher(self,filename, exprs):
        self.matcher = Matcher(exprs)
        self.matcher.tokenizer()
        self.matcher.make_astree()
        w = Watcher(filename, self.matcher.match)
        self.watcher[w.filename] = w
        t = threading.Thread(target=w.start, name = filename)
        t.daemon = True
        self.threads[v.filename] = t


    def remove_watcher(self, filename):
        key_name = path.abspath(filename)
        if key_name in self.watcher.keys():
            self.watcher[key_name].stop()
            self.threads[key_name].join()
            self.watcher.pop(key_name)
            self.threads.pop(key_name)

    def stop(self):
        for key_name in self.watcher.keys()[:]:
            self.watcher[key_name].stop()
            self.threads[key_name].join()
            self.watcher.pop(key_name)
            self.threads.pop(key_name)