import threading

class Writer:
    def writeToFile(self, filename: str, text: list[str]):
        print(f"writing to file: {filename}")
        f = open(file=filename, mode='w+', encoding='utf-8')
        try:
            for line in text:
                f.write(f"{line.strip()}\n")
        except IOError:
            print(f"failed to write to file:{filename}")
        finally:
            f.close()

    def writeToFileThread(self, filename: str, text: list[str]):
        return threading.Thread(target=self.writeToFile, kwargs={'filename': filename, 'text': text})