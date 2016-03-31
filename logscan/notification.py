import threading
import logging
from queue import Queue, Full

class Message:
    def __init__(self, users, name, path, type = None):
        self.users = users
        self.name = name
        self.path = path
        if type is None:
            self.type = ['mail',]
        self.type = type

    def __send_mail(self):
        pass

    def __send_sms(self):
        pass

    def send(self):
        for send_type in self.type:
            if send_type == 'mail':
                self.__send_mail()
            elif send_type == 'sms':
                self.__send_sms()
            else:
                raise Exception('Not Including send method {0}'.format(send_type))


class Notification:
    def __init__(self, queue):
        self.message = None
        self.__message_queue = queue
        self.__event = threading.Event()
        self.__cond = threading.Condition()

    def _send(self):
        while not self.__event.is_set:
            message = self.queue.get()
            message.send()

    def send(self):
        threading.Thread(target = self._send, name = 'send-message-real').start()
        while not self.__event.is_set():
            with self.__cond:
                self.__cond.wait()
                try:
                    self.__message_queue.put(self.message, timeout = 1)
                except Full:
                    logging.error('mail queue is full')

    def notify(self, message):
        while self.__cond:
            self.message = message
            self.__cond.notify_all()

    def start(self):
        while not self.__event.is_set():
            message = threading.Thread(target = self.send, name = 'send-message')
            message.start()

    def stop(self):
        self.__event.set()