from bin.speechRecognition import SpeechRecognition
from bin.dndGui import DnDGui

if __name__ == "__main__":
    #### TODO CREATE GUI TEST MODE
    app = DnDGui(SpeechRecognition())
    app.main_loop()