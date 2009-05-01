'''
    audio monitor thread
'''

import threading
import Queue
import time
from alsaaudio import PCM, PCM_PLAYBACK, PCM_NORMAL, PCM_FORMAT_S16_LE

class Monitor(threading.Thread):
    '''audio monitor thread'''
    def __init__(self, device, rate, period):
        threading.Thread.__init__(self)
        
        self.pcm = PCM(PCM_PLAYBACK, PCM_NORMAL, device)
        self.pcm.setformat(PCM_FORMAT_S16_LE)
        self.pcm.setchannels(2)
        self.pcm.setrate(rate)
        self.pcm.setperiodsize(period)

        self.queue = Queue.Queue(128)

        self.__stop = False

    def run(self):
        '''run loop'''
        
        while True:
            qsize = self.queue.qsize()
            
            if qsize == 0 and self.__stop:
                break
                        
            try: 
                block = self.queue.get(False)
                self.pcm.write(block)
            except Queue.Empty:        
                time.sleep(0.01)
        
    def stop(self):
        '''set stop flag'''
        self.__stop = True
