import threading
import logging
import smtplib
from queue import Queue, Full
import sqlite3

class Sender:
    def __init__(self, config):
        self.config = config

    def send_mail(self, message):
        pass

    def send_sms(self, message):
        pass


class Message:
    def __init__(self, contacts, name, count, receive_time):
        self.contacts = contacts
        self.name = name
        self.count = count
        self.receive_time = receive_time



CREATE_TABALE_DDL = r'''
CREATE TABLE IF EXISTS NOTIFICATIONS(
    id             INTEGER          PRIMARY KEY, AUTOINCREMENT,
    name           STRINGS(128)     NOT NULL,
    count          BIGINT           NOT NULL,
    contact        text             NOT NULL,
    receive_time   DATETIME         NOT NULL,
    is_send        BOOLEAN          NOT NULL DEFAULT FALSE
)'''


class Notifier:
    def __init__(self, config):
        self.config = config
        self.__sender = Sender(config)
        self.message = None
        self.__message_queue = Queue(100)
        self.__semaphore = threading.BoundedSemaphore(int(config['notification']['threads']))
        self.db = sqlite3.connect(config['notification']['persistance'])
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()
        self.__event = threading.Event()

    def notify(self, message):
        sql = r'INSERT INTO notification (name, count, contact, receive_time) VALUES(?, ?, ?, ?)'
        try:
            ret = self.cursor.execute(sql, (message.name,
                                            message.count,
                                            message.contact.dumps(),
                                            message.receive_time))
            self.db.commit()
            self.__message_queue.put_nowait(ret.lastrowid)
        except Full:
            logging.warning('notification message queue is Full')

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
