import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset

from bin.writer.writer import Writer
from bin.threadHelperFunctions import runAsThread

###############################
## https://huggingface.co/openai/whisper-large-v3
###############################

class SpeechRecognition:
    def __init__(self):
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model_id = "openai/whisper-large-v3"

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        model.to(device)

        processor = AutoProcessor.from_pretrained(model_id)

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
        )

    def process(self, sample: str, filename1: str = False, filename2: str = False):
        result = self.pipe(sample, return_timestamps="word")
        writer = Writer()
        threads = []

        if(filename1):
            threads.append(writer.writeToFileThread(filename=filename1, text=[result.get('text')]))

        if(filename2):
            chunks = []
            for chunk in result.get('chunks'):
                chunks.append(f"{chunk.get('text')};{chunk.get('timestamp')}")
            threads.append(writer.writeToFileThread(filename=filename2, text=chunks))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        return result