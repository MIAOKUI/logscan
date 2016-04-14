import threading
from queue import Queue, Empty
from .check import Checker
from .match import Matcher

class monitor:
    def __init__(self, queue, counter, notifier):
        self.queue = queue
        self.checkers = {}
        self.matchers = []
        self.rules = []
        self.counter = counter
        self.notifier = notifier
        self.checkers = {}
        self.__event = threading.Event()

    def __add_matcher(self, rule):
        matcher = Matcher(rule.name, rule.order, rule.expression).ready()
        self.matchers.append(matcher)
        self.matchers.sort(key = lambda x: x.order)

    def __add_checker(self, rule):
        checker = Checker(rule.name, rule.theshold, rule.interval, rule.contacts,self.counter, self.notifier)
        self.checkers[checker.name] = checker
        checker.start()

    def add(self, filename, name, src):
        rule = Rule.reloads(filename, name, src)
        self.rules.append(rule)
        self.__add_matcher(rule)
        self.__add_checker(rule)

    def  __remove_matcher(self, name):
        self.matchers.remove(Matcher(name, 0, ''))

    def __remove_checker(self, name):
        if name in self.checkers.keys():
            self.checkers[name].stop()
            self.checkers.pop(name)

    def remove(self,name):
        self.__remove_checker(name)
        self.__remove_checker(name)

    def __do_match(self):
        while not self.__event.is_set():
            try:
                line = self.queue.get(timeout = 0.1)
                for matcher in self.matchers:
                    if matcher(line):
                        self.counter[matcher.name] +=1
                        break
            except Empty:
                pass

    def start(self):
        self.__thread = threading.Thread(target = self.__do_match)
        self.__thread.daemon = True
        self.__thread.start()

    def stop(self):
        self.__event.set()
        if self.__thread is not None:
            self.__thread.join()