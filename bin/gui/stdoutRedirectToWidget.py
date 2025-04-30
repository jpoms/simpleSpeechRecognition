import threading
import tkinter
from bin.threadHelperFunctions import runAsThread, lockedBy

class StdoutRedirectToWidget:
    lock = threading.Lock()

    def __init__(self, text_widget: tkinter.Text, l: threading.Lock):
        self.lock = l
        self.text_widget = text_widget
        self.text_widget.config(state='disabled')
        
    @runAsThread
    @lockedBy(lock = lock, wait = True)
    def write(self, message):
        self.text_widget.config(state='normal')
        self.text_widget.insert(tkinter.END, message)
        self.text_widget.see(tkinter.END)
        
    def flush(self):
        pass