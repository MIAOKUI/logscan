import threading
import logging
import smtplib
from queue import Queue, Full

class Message:
    def __init__(self, users, name, text, type = None):
        self.users = users
        self.name = name
        self.message_text = text
        if type is None:
            self.type = ['mail',]
        self.type = type

    def _send_mail(self, domain, sender, sender_passwd):
        with smtplib.SMTP(domain) as mail:
            mail.ehlo()
            mail.starttls()
            mail.login(sender, sender_passwd)
            mail.sendmail(sender, self.users,self.message_text)

    def _send_sms(self):
        pass

    def send(self):
        for send_type in self.type:
            if send_type == 'mail':
                self._send_mail()
            elif send_type == 'sms':
                self._send_sms()
            else:
                raise Exception('Not Including send method {0}'.format(send_type))


class Notification:
    def __init__(self):
        self.message = None
        self.__message_queue = Queue()
        self.__event = threading.Event()
        self.__cond = threading.Condition()

    def _send(self):
        while not self.__event.is_set:
            message = self.__message_queue.get()
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
        with self.__cond:
            self.message = message
            self.__cond.notify_all()

    def start(self):
        message = threading.Thread(target = self.send, name = 'send-message')
        message.start()

    def stop(self):
        self.__event.set()
