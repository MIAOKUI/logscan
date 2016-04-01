import threading
import logging
from queue import Queue, Full
from .notification import Notification, Message
from .match import Matcher

class Checker:
    def __init__(self,interval, threshold, expr, users, counter, name):
        self.name = name
        self.expr = expr
        self.threshold = threshold
        self.interval = interval*60
        self.users = users
        self.counter = counter
        self.message  = None
        self.queue = Queue()
        self.__matcher = Matcher(expr).ready()
        self.__notification = Notification()
        self.__event = threading.Event()

    def check(self):
        threading.Thread(target = self.__notification.start, name = 'notification:{0}'.format(self.name))
        while not self.__event.is_set():
            self.__event.wait(self.interval)
            count = self.counter.get(self.name)
            self.counter.clean(self.name)
            if count >= self.threshold[0]:
                if count < self.threshold[1] or self.threshold[1] < 0:
                    text = '{0} matched {1} times in {2}min'.format(self.name, count, self.interval)
                    self.message = Message(self.users, self.name, text)
                    self.__notification.notify(self.message)

    def match(self):
        while not self.__event.is_set():
            line = self.queue.get()
            if self.__matcher.match(line):
                self.counter.inc(self.name)

    def start(self):
        threading.Thread(self.match,name = 'checker-match{0}'.format(self.name))
        threading.Thread(self.check, name ='checker-check{0}'.format(self.name))

    def stop(self):
        if not self.__event.is_set():
            self.__event.set()


class CheckerChain:
    def __init__(self, queue, counter):
        self.queue = queue
        self.events = {}
        self.checkers = {}
        self.line = None
        self.counter = counter
        self.__event = threading.Event()
        self.__cond = threading.Condition()

    def dispenser(self, name):
        while not self.events[name].is_set:
            with self.__cond:
                self.__cond.wait()
                try:
                    self.checkers[name].queue.put_nowait(self.line)
                except Full:
                    logging.error('checker queue {0} full'.format(name))

    def add_checker(self, users, name, expr, threshold, interval):
        self.checkers[name] = Checker(name = name,
                                      expr = expr,
                                      threshold = threshold,
                                      interval = interval,
                                      counter = self.counter,
                                      users = users)
        self.checkers[name].start()
        event = threading.Event()
        self.events[name] = event
        threading.Thread(self.dispenser, args = (name,))

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