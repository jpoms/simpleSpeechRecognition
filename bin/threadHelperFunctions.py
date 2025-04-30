import threading
from typing import Callable

def runAsThread(f: Callable):
        def wrappedFunc(*args, **kwargs):
            thread = threading.Thread(target=f, args=args, kwargs=kwargs)
            thread.start()
        return wrappedFunc

def lockedBy(lock: threading.Lock, wait: bool = False):
    def innerFunc(f: Callable):
        def wrappedFunc(*args, **kwargs):
            if(not wait and lock.locked()):
                return
            lock.acquire()
            f(*args, **kwargs)
            lock.release()
        return wrappedFunc
    return innerFunc
