import threading
import Queue
import time

class Monitor(threading.Thread):
    def __init__(self, pcm):
        threading.Thread.__init__(self)

        self.pcm = pcm
        self.queue = Queue.Queue(128)

        self.__stop = False

    def run(self):
        
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
        self.__stop = True
