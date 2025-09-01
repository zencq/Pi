import threading


class Counter(object):
    def __init__(self, start=0):
        self.lock = threading.Lock()
        self.start = start
        self.value = start

    def __str__(self) -> str:
        return str(self.value)

    def increment(self):
        self.lock.acquire()
        try:
            self.value += 1
        finally:
            self.lock.release()

    def reset(self):
        self.lock.acquire()
        try:
            self.value = self.start
        finally:
            self.lock.release()
