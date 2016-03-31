import threading
import logging
from queue import Queue, Full
from .count import Counter

def send_mail(user, message):
    pass

class Checker:
    def __init__(self, path ,interval, threshold, expr, users, counter, name):
        self.name = name
        self.expr = expr
        self.path = path
        self.threshold = threshold
        self.interval = interval*60
        self.users = users
        self.counter = counter
        self.message  = None
        self.queue = Queue()
        self.__event = threading.Event()

    def check(self):
        while not self.__event.is_set():
            self.__event.wait(self.interval)
            count = self.counter.get(self.name)
            if count > self.threshold:
                self.message = 'parameter {0}:{1} higher than threshold {2}'.format(self.name,count,self.threshold)
                self.notify()
            self.counter.clean(self.name)

    def notify(self):
        for user in self.users:
            t = threading.Thread(target = send_mail,
                                 kwargs = {'user':user, 'message':self.message},
                                 name = '{0}:{1}'.format(user, self.name))
            t.start()

    def stop(self):
        if not self.__event.is_set():
            self.__event.set()


class CheckerChain:
    def __init__(self, queue, db_path):
        self.queue = queue
        self.events = {}
        self.checkers = {}
        self.line = None
        self.counter = Counter(db_path)
        self.__event = threading.Event()
        self.__cond = threading.Condition()

    def match(self, checker):
        if not self.events[checker.name].is_set():
            line = checker.queue.get()
            if checker.match(line):
                self.counter.inc(checker.name)

    def dispense(self, checker):
        threading.Thread(target = self.match, args = (checker, )).start
        while not self.events[checker.name].is_set:
            with self.__cond:
                self.__cond.wait()
                try:
                    checker.queue.put_nowait(self.line)
                except Full:
                    logging.error('checker queue {0} full'.format(check.name))

    def add_checker(self, checker):
        self.checkers[checker.name] = checker
        checker.start()
        event = threading.Event()
        self.events[checker.name] = event
        threading.Thread(target = self.match, args = (checker, )).start

    def remove_checker(self, name):
        if name in self.checkers.keys():
            self.checkers[name].stop()
            self.events[name].set()
            self.checkers.pop(name)
            self.events.pop(name)

    def start(self):
        while not self.__event.is_set():
            self.line = self.queue.get()
            self.__cond.notify_all()

    def stop(self):
        if not self.__event.is_set():
            self.__event.set()
        for k,e in self.events.values():
            e.join()
            self.checkers[k].stop()










