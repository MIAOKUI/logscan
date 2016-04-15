import shelve
import threading

class OffsetPersistance:
    def __init__(self, config):
        self.config = config
        self.__lock = threading.Lock()
        self.__db = shelve.open(config['main']['offset_db'])

    def put(self, filename, offset):
        with self.__lock:
            self.__db[filename] = offset

    def get(self, filename):
        with self.__lock:
            return(self.__db.get(filename, 0))

    def sync(self):
        with self.__lock:
            self.__db.sync()

    def close(self):
        with self.__lock:
            self.__db.close()