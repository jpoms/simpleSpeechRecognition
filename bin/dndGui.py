import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from enum import Enum
import os
import threading
from typing import Callable

from bin.speechRecognition import SpeechRecognition
from bin.threadHelperFunctions import lockedBy, runAsThread

class GuiStates(Enum):
    WAIT_FOR_INPUT = 1
    READY_INPUT = 2
    PROCESSING_INPUT = 3


class DnDGui:
    state = GuiStates.WAIT_FOR_INPUT
    busy = threading.Lock()
    root = TkinterDnD.Tk()
    filename = ''

    ### FUNC DECORATORS
    def runThread(f: Callable):
        def wrappedFunc(self, *args, **kwargs):
            ## ditch actions while busy to avoid overloading the app
            if(self.busy.locked()):
                return
            thread = threading.Thread(target=f, args=(self, *args), kwargs=kwargs)
            thread.start()
        return wrappedFunc

    def lockBusy(f: Callable):
        def wrappedFunc(self, *args, **kwargs):
            self.busy.acquire()
            f(self, *args, **kwargs)
            self.busy.release()
        return wrappedFunc

    ### INIT
    def __init__(self, sR: SpeechRecognition):
        self.sR = sR
        # add widgets
        self.content = tk.Frame(self.root, padx=9, pady=9)
        self.titleLabel = tk.Label(self.content, text = "SPEECH TO TEXT", padx=3, pady=3, width=90)
        self.labelDnD = tk.Label(self.content, text = ">> Drag and Drop Mp3 File <<", padx=3, pady=3, width=90, height = 10, relief="sunken")
        self.runButton = tk.Button(self.content, text= ">> RUN <<", padx=9, pady=3, width=40, relief="solid", state="disabled")
        self.resetButton = tk.Button(self.content, text= ">> RESET <<", padx=9, pady=3, width=40, relief="solid", state="active")

        # define grid geometry
        self.content.grid(row=0, column=0, sticky='NESW')
        self.titleLabel.grid(row=0, column=0, pady=2, sticky='ESW', columnspan=2)
        self.labelDnD.grid(row=1, column=0, pady=2, sticky='NESW', columnspan=2)
        self.runButton.grid(row=2, column=0, pady=2, sticky='NEW', columnspan=1)
        self.resetButton.grid(row=2, column=1, pady=2, sticky='NEW', columnspan=1)

        # define resize behaviour
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)
        self.content.columnconfigure(1, weight=1)
        self.content.rowconfigure(0, weight=1)
        self.content.rowconfigure(1, weight=5)
        self.content.rowconfigure(2, weight=1)

        # bind events
        self.labelDnD.drop_target_register(DND_FILES)
        self.labelDnD.dnd_bind('<<Drop>>', self.handle_drop)
        self.runButton.config(command=self.submitRun)
        self.resetButton.config(command=self.submitReset)

    ### HANDLE STATES
    def handleStateChange(self, state: GuiStates):
        # check valid state change
        if (not(self.state == GuiStates.WAIT_FOR_INPUT and state == GuiStates.PROCESSING_INPUT or 
                self.state == GuiStates.PROCESSING_INPUT and state == GuiStates.WAIT_FOR_INPUT or
                self.state == GuiStates.PROCESSING_INPUT and state == GuiStates.PROCESSING_INPUT)):
            self.state = state
            self.setConfigForGuiState(state)
        else:
            messagebox.showerror(title="INVALID STATE CHANGE", message="UNKNOWN STATE CHANGE")
            raise Exception("INVALID STATE CHANGE - UNKNOWN STATE CHANGE")
    
    def setConfigForGuiState(self, state: GuiStates):
        if(state==GuiStates.WAIT_FOR_INPUT):
            self.state = state
            self.runButton.config(state="disabled")
            self.resetButton.config(state="active")
        elif(state==GuiStates.READY_INPUT):
            self.state = state
            self.runButton.config(state="active")
            self.resetButton.config(state="active")
        elif(state==GuiStates.PROCESSING_INPUT):
            self.state = state
            self.runButton.config(state="disabled")
            self.resetButton.config(state="disabled")
        else:
            messagebox.showerror(title="INVALID STATE CHANGE", message="COULDNT SET CONFIG FOR STATE")
            raise Exception("INVALID STATE CHANGE - COULDNT SET CONFIG FOR STATE")

    ### EVENT HANDLER
    @runAsThread
    @lockedBy(busy)
    def handle_drop(self, event):
        files = self.root.splitlist(event.data)
        # Filter for MP3 files and add to listbox
        foundAtLeastOne=False
        self.labelDnD.config(text=">> Drag and Drop Mp3 File <<")
        for file in files:
            if file.lower().endswith('.mp3'):
                foundAtLeastOne=True
                currentLabel = self.labelDnD.cget("text")
                filename = os.path.abspath(file)
                self.labelDnD.config(text=f"{currentLabel}\n{filename}")
                self.filename = filename
                break
        if foundAtLeastOne: self.handleStateChange(GuiStates.READY_INPUT)

    @runAsThread
    @lockedBy(busy)
    def submitRun(self):
        self.handleStateChange(GuiStates.PROCESSING_INPUT)
        result = self.sR.process(self.filename)
        ###### TODO PROVIDE MEANINGFUL OUTPUT
        print(result)
        self.handleStateChange(GuiStates.READY_INPUT)

    @runAsThread
    @lockedBy(busy)
    def submitReset(self):
        self.filename = ''
        self.labelDnD.config(text=">> Drag and Drop Mp3 File <<")
        self.handleStateChange(GuiStates.WAIT_FOR_INPUT)

    ### GUI MAIN LOOP
    def main_loop(self):
        self.root.mainloop()