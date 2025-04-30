from bin.speechRecognition import SpeechRecognition
from bin.gui.dndGui import DnDGui
import sys

if __name__ == "__main__":
    #### TODO CREATE GUI TEST MODE
    app = DnDGui(SpeechRecognition())
    sys.stdout = app.stdoutTextBox
    app.main_loop()
