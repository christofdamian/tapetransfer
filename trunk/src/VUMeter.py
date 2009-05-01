'''
progress bar class for the vumeter
'''

import progressbar
import time

class VUMeter(progressbar.ProgressBar):
    '''extended progress bar'''
    
    rms    = 0
    maxamp = 0
    
    def __init__(self, maxval):
        widgets = [
          "[",RMS(),
          "][",TimeSinceStart(),
          "][",MaxAmplitude(),
          "][", progressbar.Bar(marker=progressbar.RotatingMarker()),"]"]
        progressbar.ProgressBar.__init__(
                                         self, 
                                         maxval = maxval, 
                                         widgets = widgets)

    
    def _need_update(self):
        '''update progress bar if percentage or maxamp changed'''
        if int(self.percentage()) != int(self.prev_percentage):
            return True
        return self.maxamp == 0


class RMS(progressbar.ProgressBarWidget):
    '''RMS display widget'''
    def update(self, pbar):
        '''update widget'''
        return "R:%5d" % pbar.rms

class MaxAmplitude(progressbar.ProgressBarWidget):
    '''Max amplitude widget'''
    def update(self, pbar):
        '''update widget'''
        if pbar.maxamp == pbar.maxval:
            return "CLIPPED!"
        
        return "M:%2.2f%%" % (pbar.maxamp * 100.0 / pbar.maxval)

class TimeSinceStart(progressbar.ProgressBarWidget):
    '''time since start widget'''
    @staticmethod
    def format_time(seconds):
        '''nice time format'''
        return time.strftime('%H:%M:%S', time.gmtime(seconds))

    def update(self, pbar):
        '''update widget'''
        return 'T:%s' % self.format_time(pbar.seconds_elapsed)
