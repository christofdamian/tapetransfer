#!/usr/bin/python
#
# tapetransfer
#
# simple text mode audio recorder, with VU meter, and clip/max amplitude meter.
#
# copyright 2008 christof@damian.net
# copyright 2006 duncan@zog.net.au
# released under the GPL as per http://www.gnu.org/copyleft/gpl.html
#
# Needs pyalsaaudio : http://www.wilstrup.net/pyalsaaudio/
# Needs progressbar : http://cheeseshop.python.org/pypi/progressbar
#
# to do: set sound card options (bit rate, etc) on command line
# package for debian (including the components it needs)
#
# modified from: http://blog.zog.net.au/index.cgi/nerdy/kissrec/index.html by 
# duncan@zog.net.au
#

VERSION = 0.2

import alsaaudio
import sys
import time
import optparse
import termios, fcntl, os
import progressbar, audioop
from Queue import Queue
from Writer import WavWriter

maxamp = 0
rms = 0
key = "none"
queue = Queue(128)



class MyProgressBar(progressbar.ProgressBar):
    '''extended progress bar'''
    def _need_update(self):
        '''update progress bar if percentage or maxamp changed'''
        if int(self.percentage()) != int(self.prev_percentage):
            return True
        return maxamp == 0


class RMS(progressbar.ProgressBarWidget):
    '''RMS display widget'''
    def update(self, pbar):
        '''update widget'''
        return "R:%5d" % rms

class MaxAmplitude(progressbar.ProgressBarWidget):
    '''Max amplitude widget'''
    def update(self, pbar):
        '''update widget'''
        if maxamp == 32768:
            return "CLIPPED!"
        else:
            return "M:%2.2f%%" % (maxamp / 32768.0 * 100)

class TimeSinceStart(progressbar.ProgressBarWidget):
    '''time since start widget'''
    @staticmethod
    def format_time(seconds):
        '''nice time format'''
        return time.strftime('%H:%M:%S', time.gmtime(seconds))

    def update(self, pbar):
        '''update widget'''
        return 'T:%s' % self.format_time(pbar.seconds_elapsed)

#
# parse command line args
#
usage = "usage: %prog [options] outputfile.wav"
parser = optparse.OptionParser(usage, version="%prog "+"%f" % VERSION)
parser.add_option("-d", "--device", dest="device",
                  help="ALSA device to use, e.g. default for default device",
		  default="default")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose")
(options, args) = parser.parse_args()

# code from pyalsaaudio record demo, plys python FAQ material non non blocking 
# keyboard detect under linux
rate = 48000

# open ALSA sound card device, non blocking
if options.verbose:
    print "opening alsa PCM device ", options.device
inp = alsaaudio.PCM(
                    alsaaudio.PCM_CAPTURE, 
                    alsaaudio.PCM_NONBLOCK, 
                    options.device)
inp.setchannels(2)
inp.setrate(rate)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
inp.setperiodsize(2000)

outp = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NONBLOCK, "default")
outp.setchannels(2)
outp.setrate(rate)
outp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
outp.setperiodsize(2000)


if options.verbose:
    print "tapetransfer ", VERSION
    print
    print "controls:"
    print "   <Enter>     to quit recording"
    print "   <space bar> to reset peak counter"
    print
    print "recording to wav file ", args[0]

widgets = [
    "[",RMS(),
    "][",TimeSinceStart(),
    "][",MaxAmplitude(),
    "][", progressbar.Bar(marker=progressbar.RotatingMarker()),"]"]

pbar = MyProgressBar(widgets=widgets, maxval=2**15 + 2).start()

# set input into mon blocking key detect mode
stdinfd = sys.stdin.fileno()
oldterm = termios.tcgetattr(stdinfd)
newattr = termios.tcgetattr(stdinfd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(stdinfd, termios.TCSANOW, newattr)

oldflags = fcntl.fcntl(stdinfd, fcntl.F_GETFL)
fcntl.fcntl(stdinfd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

recording = False
quiet = 0

writer = WavWriter(args[0], rate, queue)
writer.start()

try:
    
    while key != '\n' and not (recording and quiet > 30):
        
        # Read data from device
        l, data = inp.read()
     
        if l > 0:
            rms = audioop.rms(data, 2) 

            if rms > 150:
                quiet = 0
            else:
                quiet += 1

            if quiet == 0 and not recording:
                recording = True
                pbar.start_time = None  
                

            if recording:
                queue.put(data,1) 
                                
                audiomax = audioop.max(data, 2)
                if audiomax > maxamp:
                    maxamp = audiomax
                pbar.update(audiomax)
    
                
                try:
                    outp.write(data)
                except alsaaudio.ALSAAudioError:
                    print "data",l

        if recording and l < 0:
            print "\nl =",l 
       
        # detect key
        try:
            key = sys.stdin.read(1)
            if key == ' ':
                maxamp = 0
                pbar.update(0)
        except IOError:
            pass

        #time.sleep(0.01)

finally:
    termios.tcsetattr(stdinfd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(stdinfd, fcntl.F_SETFL, oldflags) 

pbar.finish()

writer.stop()
writer.join()

if options.verbose:
    print "wav file ", args[0], " written."

print "maxqueue ", writer.maxqueue

