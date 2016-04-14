class Counter:
    def __init__(self):
        self.db = {}

    def inc(self, name):
        self.db[name] = self.db.get(name, 0) + 1

    def get(self, name):
        return self.db.get(name)

    def clean(self, name):
        self.db.pop(name)
