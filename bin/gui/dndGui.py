import tkinter as tk
from tkinter import messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import threading

from bin.gui.stdoutRedirectToWidget import StdoutRedirectToWidget
from bin.gui.dndGuiStates import DndGuiStates as STATE
from bin.speechRecognition import SpeechRecognition
from bin.threadHelperFunctions import lockedBy, runAsThread

class DnDGui:
    state = STATE.WAIT_FOR_INPUT
    busy = threading.Lock()
    printLock = threading.Lock()
    root = TkinterDnD.Tk()
    root.title = "SimpleSpeechRecognition"
    filename = ''

    ### INIT
    def __init__(self, sR: SpeechRecognition):
        self.sR = sR
        self.root.title = 'SimpleSpeechRecognition'
        self.root.geometry('860x480')
        # add widgets
        self.buttons = tk.Frame(self.root, padx=9, pady=9, width = 30)
        self.content = tk.Frame(self.root, padx=9, pady=9, width = 70)

        self.printText = tk.Text(self.content, padx=9, pady=3, width=70)

        self.titleLabel = tk.Label(self.buttons, text = "SPEECH TO TEXT", padx=3, pady=3, width=30)
        self.labelDnD = tk.Label(self.buttons, text = ">> Drag and Drop Mp3 File <<", padx=3, pady=3, width=30, height = 10, relief="sunken")

        self.outFileName1Frame = tk.Frame(self.buttons, padx=3, pady=1, width = 70, height=3)
        self.outFileName1Label = tk.Label(self.outFileName1Frame, text = "File only text", padx=9, width=12)
        self.outFileName1 = tk.StringVar()
        self.outFileName1Input = tk.Entry(self.outFileName1Frame, textvariable=self.outFileName1, state="readonly")

        self.outFileName2Frame = tk.Frame(self.buttons, padx=3, pady=1, width = 70, height=3)
        self.outFileName2Label = tk.Label(self.outFileName2Frame, text = "File text and timing", padx=9, width=12)
        self.outFileName2 = tk.StringVar()
        self.outFileName2Input = tk.Entry(self.outFileName2Frame, textvariable=self.outFileName2, state="readonly")

        self.runButton = tk.Button(self.buttons, text= ">> RUN <<", padx=9, pady=3, width=15, relief="solid", state="disabled")
        self.resetButton = tk.Button(self.buttons, text= ">> RESET <<", padx=9, pady=3, width=15, relief="solid", state="active")

        # define grid geometry
        self.printText.grid(row=0, column=0, sticky="NESW")
        self.content.grid(row=0, column=0, sticky='NESW')
        self.buttons.grid(row=0, column=1, sticky='NESW')
        self.titleLabel.grid(row=0, column=0, pady=2, sticky='ESW', columnspan=2)
        self.labelDnD.grid(row=1, column=0, pady=2, sticky='NESW', columnspan=2)
        self.outFileName1Frame.grid(row=2, column=0, pady=2, sticky='NESW', columnspan=2)
        self.outFileName1Label.grid(row=0, column=0, pady=2, sticky='NESW', columnspan=1)
        self.outFileName1Input.grid(row=0, column=1, pady=2, sticky='NESW', columnspan=1)
        self.outFileName2Frame.grid(row=3, column=0, pady=2, sticky='NESW', columnspan=2)
        self.outFileName2Label.grid(row=0, column=0, pady=2, sticky='NESW', columnspan=1)
        self.outFileName2Input.grid(row=0, column=1, pady=2, sticky='NESW', columnspan=1)
        self.runButton.grid(row=4, column=0, pady=2, sticky='NEW', columnspan=1)
        self.resetButton.grid(row=4, column=1, pady=2, sticky='NEW', columnspan=1)

        # define resize behaviour
        self.root.columnconfigure(0, weight=6)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.buttons.columnconfigure(0, weight=1)
        self.buttons.columnconfigure(1, weight=1)
        self.buttons.rowconfigure(0, weight=1)
        self.buttons.rowconfigure(1, weight=3)
        self.buttons.rowconfigure(2, weight=1)
        self.buttons.rowconfigure(3, weight=1)
        self.buttons.rowconfigure(4, weight=1)
        self.outFileName1Frame.rowconfigure(0, weight=1)
        self.outFileName1Frame.columnconfigure(0, weight=1)
        self.outFileName1Frame.columnconfigure(1, weight=1)
        self.outFileName2Frame.rowconfigure(0, weight=1)
        self.outFileName2Frame.columnconfigure(0, weight=1)
        self.outFileName2Frame.columnconfigure(1, weight=1)
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        # bind
        self.labelDnD.drop_target_register(DND_FILES)
        self.labelDnD.dnd_bind('<<Drop>>', self.handle_drop)
        self.runButton.config(command=self.submitRun)
        self.resetButton.config(command=self.submitReset)
        self.stdoutTextBox = StdoutRedirectToWidget(self.printText, self.printLock)

    ### HANDLE STATES
    def handleStateChange(self, state: STATE):
        # check valid state change
        if (not(self.state == STATE.WAIT_FOR_INPUT and state == STATE.PROCESSING_INPUT or 
                self.state == STATE.PROCESSING_INPUT and state == STATE.WAIT_FOR_INPUT or
                self.state == STATE.PROCESSING_INPUT and state == STATE.PROCESSING_INPUT)):
            self.state = state
            self.setConfigForGuiState(state)
        else:
            messagebox.showerror(title="INVALID STATE CHANGE", message="UNKNOWN STATE CHANGE")
            raise Exception("INVALID STATE CHANGE - UNKNOWN STATE CHANGE")

    def setConfigForGuiState(self, state: STATE):
        if(state==STATE.WAIT_FOR_INPUT):
            self.state = state
            self.filename = ''
            self.labelDnD.config(text=">> Drag and Drop Mp3 File <<")
            self.runButton.config(state="disabled")
            self.resetButton.config(state="active")
            self.outFileName1Input.config(state="readonly")
            self.outFileName2Input.config(state="readonly")
            self.outFileName1.set('')
            self.outFileName2.set('')
        elif(state==STATE.READY_INPUT):
            self.state = state
            self.runButton.config(state="active")
            self.resetButton.config(state="active")
            self.outFileName1Input.config(state="normal")
            self.outFileName2Input.config(state="normal")
        elif(state==STATE.PROCESSING_INPUT):
            self.state = state
            self.runButton.config(state="disabled")
            self.resetButton.config(state="disabled")
            self.outFileName1Input.config(state="readonly")
            self.outFileName2Input.config(state="readonly")
        else:
            messagebox.showerror(title="INVALID STATE CHANGE", message="COULDNT SET CONFIG FOR STATE")
            raise Exception("INVALID STATE CHANGE - COULDNT SET CONFIG FOR STATE")

    ### EVENT HANDLER
    @runAsThread
    @lockedBy(lock = busy)
    def handle_drop(self, event):
        files = self.root.splitlist(event.data)
        # Filter for MP3 files and add to listbox
        foundAtLeastOne=False
        self.labelDnD.config(text=">> Drag and Drop Mp3 File <<")
        for file in files:
            if file.lower().endswith('.mp3'):
                # TODO expand for batch processing
                foundAtLeastOne=True
                currentLabel = self.labelDnD.cget("text")
                filename = os.path.abspath(file)
                self.labelDnD.config(text=f"{currentLabel}\n{os.path.basename(filename)}")
                self.outFileName1.set(f"{filename.split('.')[0]}_text.txt")
                self.outFileName2.set(f"{filename.split('.')[0]}_text_time.txt")
                self.filename = filename
                break
        if foundAtLeastOne: self.handleStateChange(STATE.READY_INPUT)

    @runAsThread
    @lockedBy(lock = busy)
    def submitRun(self):
        self.handleStateChange(STATE.PROCESSING_INPUT)
        result = self.sR.process(sample=self.filename, 
                        filename1=self.outFileName1.get(), 
                        filename2=self.outFileName2.get())
        print(f"result: {result.get('text')}")
        self.handleStateChange(STATE.READY_INPUT)

    @runAsThread
    @lockedBy(lock = busy)
    def submitReset(self):
        self.handleStateChange(STATE.WAIT_FOR_INPUT)

    ### GUI MAIN LOOP
    def main_loop(self):
        self.root.mainloop()