#!/usr/bin/python
#
# KISS record
#
# simple text mode audio recorder, with VU meter, and clip/max amplitude meter.
#
# copyright 2006 duncan@zog.net.au, released under the GPL as per http://www.gnu.org/copyleft/gpl.html
#
# Needs pyalsaaudio : http://www.wilstrup.net/pyalsaaudio/
# Needs progressbar : http://cheeseshop.python.org/pypi/progressbar
#
# to do: set sound card options (bit rate, etc) on command line
# package for debian (including the components it needs)
#
VERSION=0.1

import alsaaudio
import sys
import time
import wave
import optparse
import termios, fcntl, sys, os
import progressbar, audioop


maxamp = 0

key = "none"

# extend need update to also update if maxamp changes
class myprogressbar(progressbar.ProgressBar):

   def _need_update(self):
      return int(self.percentage()) != int(self.prev_percentage) or maxamp == 0


class MaxAmplitude(progressbar.ProgressBarWidget):

   def update(self, pbar):
      if maxamp == 32768:
         return "CLIPPED!"
      else:
         return "M:%2.2f%%" % (maxamp / 32768.0 * 100)


class TimeSinceStart(progressbar.ProgressBarWidget):
   def format_time(self, seconds):
      return time.strftime('%H:%M:%S', time.gmtime(seconds))

   def update(self, pbar):
      return 'T:%s' % self.format_time(pbar.seconds_elapsed)

#
# parse command line args
#
usage = "usage: %prog [options] outputfile.wav"
parser = optparse.OptionParser(usage,version="%prog "+"%f" % VERSION)
parser.add_option("-d", "--device", dest="device",
                  help="ALSA device to use, e.g. default for default device, or hw:1 for second sound card",
		  default="default")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose")
(options, args) = parser.parse_args()

# code from pyalsaaudio record demo, plys python FAQ material non non blocking 
# keyboard detect under linux

# open ALSA sound card device, non blocking
if options.verbose:
   print "opening alsa PCM device ",options.device
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK,options.device)

inp.setchannels(2)
inp.setrate(44100)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

inp.setperiodsize(2000)

# get output wav file ready, same params as the PCM input
wfile = wave.open(args[0],'w')
wfile.setparams((2,2,44100,0,'NONE',''))

if options.verbose:
   print "KEEP IT SIMPLE ALSA AUDIO RECORDER 2006 duncan@zog.net.au version ",VERSION
   print
   print "controls:"
   print "   <Enter>     to quit recording"
   print "   <space bar> to reset peak counter"
   print
   print "recording to wav file ",args[0]

widgets = ["[",TimeSinceStart(),"][",MaxAmplitude(),'][', progressbar.Bar(marker=progressbar.RotatingMarker()),']']

pbar = myprogressbar(widgets=widgets,maxval=2**15 + 2).start()

# set input into mon blocking key detect mode
stdinfd = sys.stdin.fileno()
oldterm = termios.tcgetattr(stdinfd)
newattr = termios.tcgetattr(stdinfd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(stdinfd, termios.TCSANOW, newattr)

oldflags = fcntl.fcntl(stdinfd, fcntl.F_GETFL)
fcntl.fcntl(stdinfd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

try:
   while key != '\n':
     # Read data from device
     l,data = inp.read()
     
     if l:
       wfile.writeframesraw(data)
       max = audioop.max(data,2)
       if max > maxamp:
	  maxamp = max
       pbar.update(max)

     # detect key
     try:
         key = sys.stdin.read(1)
	 if key == ' ':
	    maxamp = 0
	    pbar.update(0)
     except IOError:
        pass

     time.sleep(0.02)

finally:
    termios.tcsetattr(stdinfd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(stdinfd, fcntl.F_SETFL, oldflags) 

pbar.finish()
wfile.close()
if options.verbose:
   print "wav file ",args[0]," written."

