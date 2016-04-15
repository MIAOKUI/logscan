import threading
import logging
from queue import Queue, Full, Empty
import sqlite3

class MailSender:
    def __init__(self, config):
        self.config = config

    def send_mail(self, message):
        pass

class SMSSender:
    def __init__(self, config):
        self.config = config

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
        self.__sender = [MailSender[config], SMSSender[config]]
        self.message = None
        self.__message_id_queue = Queue(100)
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
            self.__message_id_queue.put_nowait(ret.lastrowid)
        except Full:
            logging.warning('notification message queue is Full')
        except Exception as e:
            self.db.rollback()
            logging.error('Persistance message failed, {0}'.format(e))

    def __send_wrap(self, sender, message):
        with self.__semaphore:
            sender(message)

    def __send(self):
        while not self.__event.is_set():
            try:
                row_id = self.__message_id_queue.get(timeout=100)
                self.cursor.execute(r'SELECT name, count, contact, receive_time, is_send'
                                    r'FROM notification WHERE rowid = ?',
                                    (row_id,))
                row = self.cursor.fetchone()
                if row['is_send']:
                    continue
                message = Message(**row)
                for sender in self.__sender:
                    t = threading.Thread(self.__send_wrap, (sender, message),
                                         name='sender-{0}'.format(sender.__name__))
                    t.daemon = True
                    t.start()
                self.cursor.execute('UPDATE notification SET is_send =? WHERE row_id=?', (True, row_id))
                self.db.commit()
            except Empty:
                self.__event.wait(100)

    def __compensate(self):
        self.cursor.execute(r'SELECT rowid FROM notification WHERE is_send = ?', (False, ))
        for row in self.cursor.fetchall():
            self.__message_id_queue.put_nowait(row)

    def __compensation(self):
        while not self.__event.is_set():
            self.__event.wait(60)
            self.__compensate()

    def start(self):
        self.__compensate()
        st = threading.Thread( target=self.__send, name = 'notifier-send-thread')
        st.daemon = True
        st.start()
        ct = threading.Thread(target = self.__compensation, name = 'notifier-compensation-thread')
        ct.daemon = True
        ct.start()

    def stop(self):
        self.__event.set()
        self.cursor.close()
        self.db.commit()
        self.db.close()
