import wave
import threading
from Queue import Queue
import time

class WavWriter(threading.Thread):
    def __init__(self, filename, rate, queue):
        threading.Thread.__init__(self)

        self.filename = filename
        self.rate = rate
        self.queue = queue

        self.__stop = False
        self.maxqueue = 0

    def run(self):
        wav = wave.open(self.filename, 'w')
        wav.setparams((2, 2, self.rate, 0, 'NONE', ''))
        
        while True:
            qsize = self.queue.qsize()
 
            if qsize == 0 and self.__stop:
                break
            
            if qsize > self.maxqueue:
                self.maxqueue = qsize 
            
            block = self.queue.get(1)
            wav.writeframesraw(block)
            time.sleep(0.02)
        
        wav.close()
        
    def stop(self):
        self.__stop = True
