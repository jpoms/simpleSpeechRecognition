import argparse
import sys

from bin.speechRecognition import SpeechRecognition
from bin.gui.dndGui import DnDGui

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='SimpleSpeechRecognition',
                    description='Uses model from huggingFace to translate speech from audiofile to text')
    
    parser.add_argument('--no-gui', action='store_true', required=False)
    parser.add_argument('--sample', '-s', type=str, required=False)

    appArgs = vars(parser.parse_args())

    if(appArgs.get('no_gui') and appArgs.get('sample')):
        app = SpeechRecognition()
        sampleFile = appArgs.get('sample')
        result = app.process(sample=sampleFile, 
                             filename1=f"{sampleFile.split('.')[0]}_text.txt", 
                             filename2=f"{sampleFile.split('.')[0]}_text_time.txt")
        print(result)
    elif(appArgs.get('no_gui') and not appArgs.get('sample')):
         parser.error("<sample> required with --no-gui")
    else:
        app = DnDGui(SpeechRecognition())
        sys.stdout = app.stdoutTextBox
        app.main_loop()