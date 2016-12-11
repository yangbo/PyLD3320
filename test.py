from ld3320 import LD3320
import RPi.GPIO as GPIO
import time

print("GPIO version: %s\n" % GPIO.VERSION)

pin_int = 3
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_int, GPIO.IN, pull_up_down=GPIO.PUD_UP)

ld3320 = LD3320(port=0, device=0)
ld3320.initASR()
print("idle? %s" % ld3320.isASRIdle())

keywords = ['kai deng', 'guan deng', 'qing guan deng','yang bo', 'yang yi lin', 'peng jin']
#keywords = ['yang bo', 'yang yi lin', 'peng jin']
for index in range(len(keywords)):
  result = ld3320.addKeyword(index, keywords[index])
  print("Add keywod [%d] '%s' %s" % (index, keywords[index], 'ok' if result else 'fail'))

print("Please speak ...")
try:
  while True:
    result = ld3320.runASR()
    print("Start ASR %s" % 'ok' if result else 'fail')
    GPIO.wait_for_edge(pin_int, GPIO.FALLING)
    (found,index) = ld3320.handleInterrupt()
    print("Interrupt received, find recognize result...")
    if found:
      print("keyword is '%s', index=%s" % (keywords[index], index))
    else:
      print("Can not recognize.")
except:
  print("killed by keyboard")
GPIO.cleanup()

