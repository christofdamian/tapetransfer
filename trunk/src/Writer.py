import wave
import threading
from Queue import Queue
import time

class WavWriter(threading.Thread):
    def __init__(self, filename, rate, queue):
        threading.Thread.__init__(self)

        self.__stop = False
        self.wav = wave.open(filename, 'w')
        self.wav.setparams((2, 2, rate, 0, 'NONE', ''))
        self.maxqueue = 0
        self.queue = queue

    def run(self):
        while True:
            qsize = self.queue.qsize()
            if qsize == 0 and self.__stop:
                break
            
            if qsize > self.maxqueue:
                self.maxqueue = qsize 
            block = self.queue.get(1)
            self.wav.writeframesraw(block)
            time.sleep(0.02)
        self.wav.close()
        
    def stop(self):
        self.__stop = True
