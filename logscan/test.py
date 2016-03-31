import threading
import logging
import time

logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s %(levelname)s [%(threadName)s] %(message)s')

def worker(event):
    event.wait(6)
    logging.debug("event is set")


def set(event):
    time.sleep(2)
    event.set()
    logging.debug("event is set")

class Message:
    def __init__(self, message):
        self.message = message

def consumer(cond, message):
    with cond:
        cond.wait()
        logging.debug("consumer {0}".format(message.message))

def producer(cond, message):
    with cond:
        time.sleep(10)
        message.message = 'ha ha ha'
        logging.debug("producer {0}".format(message.message))
        cond.notify_all()






if __name__ == '__main__':
    # event = threading.Event()
    #
    # w = threading.Thread(target=worker, args=(event, ), name='worker')
    # w.start()
    #
    # s = threading.Thread(target=set, args=(event, ), name='set')
    # s.start()
    message = Message(None)
    cond = threading.Condition()
    c1 = threading.Thread(target = consumer, args = (cond, message), name = 'consumer-1')
    c1.start()

    c2 = threading.Thread(target = consumer, args = (cond, message), name = 'consumer-2')
    c2.start()

    p = threading.Thread(target = producer, args = (cond, message), name = 'producer')
    p.start()

    print(message.message)