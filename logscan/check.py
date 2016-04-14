import threading
from .notification import Notification, Message

class Checker:
    def __init__(self, name, threshold, interval, contacts, counter, notifier):
        self.name = name
        self.threshold = threshold
        self.interval = interval
        self.contacts = contacts
        self.counter = counter
        self.notifier = notifier
        self.__event = threading.Event()

    def __do_check(self):
        # begin checking, based on interval
        while not self.__event.is_set():
            self.__event.wait(self.interval)
            count = self.counter.get(self.name)
            self.counter.clean(self.name)
            if count >= self.threshold[0]*60:
                if count < self.threshold[1]*60 or self.threshold[1]*60 < 0:
                    text = '{0} matched {1} times in {2}min'.format(self.name, count, self.interval)
                    self.message = Message(self.users, self.name, text)
                    self.__notify(self.message)

    def start(self):
        # start match match thread and check thread
        threading.Thread(self.__do_check,name = 'checker_{0}'.format(self.name))

    def __notify(self, message):
        self.notifier.notify(message)


    def stop(self):
        if not self.__event.is_set():
            self.__event.set()
