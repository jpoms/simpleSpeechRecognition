import threading
from typing import Callable

def runAsThread(f: Callable):
        def wrappedFunc(*args, **kwargs):
            thread = threading.Thread(target=f, args=args, kwargs=kwargs)
            thread.start()
        return wrappedFunc

def lockedBy(l: threading.Lock):
    def innerFunc(f: Callable):
        def wrappedFunc(*args, **kwargs):
            ## TODO make it visible somehow that actions are ignored as long as the lock is not released.
            if(l.locked()):
                return
            l.acquire()
            f(*args, **kwargs)
            l.release()
        return wrappedFunc
    return innerFunc
