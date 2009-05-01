'''
wav file writer thread
'''

import wave
import threading
import Queue
import time

class WavWriter(threading.Thread):
    '''wav file writer thread'''
    def __init__(self, filename, rate):
        threading.Thread.__init__(self)

        self.filename = filename
        self.rate = rate
        self.queue = Queue.Queue(128)

        self.__stop = False
        self.maxqueue = 0

    def run(self):
        '''run loop'''
        wav = wave.open(self.filename, 'w')
        wav.setparams((2, 2, self.rate, 0, 'NONE', ''))
        
        while True:
            qsize = self.queue.qsize()
            
            if qsize == 0 and self.__stop:
                break
            
            if qsize > self.maxqueue:
                self.maxqueue = qsize 
            
            try: 
                block = self.queue.get(False)
                wav.writeframesraw(block)
            except Queue.Empty:
                time.sleep(0.01)
        
            time.sleep(0.01)
        
        wav.close()
        
    def stop(self):
        '''set stop flag'''
        self.__stop = True
