from gpiozero import *
import time


class LD3320(SPIDevice):
  """
  LD3320 SPI device driver.
  Author: Bob Yang (bob.yang.dev@gmail.com)
  Pins:
      Reset -> GPIO2
  """

  
  def __init__(self, **spi_args):
    super(LD3320, self).__init__(clock_pin=11, mosi_pin=10, miso_pin=9, select_pin=8)
    print("spi device: " + str(self._spi._device))
    spi = self._spi
    spi._device.max_speed_hz = 1500000
    spi._device.no_cs = True
    spi.clock_mode = 0b10
    spi.bits_per_word = 8
    spi.lsb_first = False

  def read(self, reg):
    return self._spi.transfer([0x05,reg,0])[2]

  def write(self, reg, data):
    self._spi.write([0x04, reg, data])
    
  def reset(self):
    "Reset LD3320 registers"
    reset = DigitalOutputDevice(2, True, True)
    reset.on()
    time.sleep(0.001)
    reset.off()
    time.sleep(0.001)
    reset.on()
    reset.close()
    print("Reset LD3320 done.")

  def read_print(self, reg):
    data = self.read(reg)
    print("read %s" % hex(data))
    return data

  def test(self):
    ld3320.reset()
    b1 = ld3320.read_print(0x06)
    b2 = ld3320.read_print(0x06)
    b3 = ld3320.read_print(0x35)
    b4 = ld3320.read_print(0xb3)
    if (b1==0x87 or b1==0x00) and \
        b2==0x87 and b3==0x80 and b4==0xFF:
      print("Read register pass.")
    else:
      print("Read register fail!")

    ld3320.write(0x35,0x33)
    print("write 0x33")
    ld3320.write(0x1b,0x55)
    print("write 0x55")
    ld3320.write(0xb3,0xaa)
    print("write 0xaa")
    ld3320.read_print(0x35)
    ld3320.read_print(0x1b)
    ld3320.read_print(0xb3)
    ld3320.close()

  def delay(self, ms):
    time.sleep(0.001*ms)

  def commonInit(self, nLD_Mode='MODE_ASR'):
    """ Common Circuit initialization."""
    # constants
    CLK_IN = 22.1184 # user need modify this value according to clock in
    LD_PLL_11=round((CLK_IN/2.0)-1)
    LD_PLL_MP3_19=0x0f
    LD_PLL_MP3_1B=0x10
    LD_PLL_MP3_1D=round(((90.0*((LD_PLL_11)+1))/(CLK_IN))-1)
    LD_PLL_ASR_19=round(CLK_IN*32.0/(LD_PLL_11+1) - 0.51)
    LD_PLL_ASR_1B=0x48
    LD_PLL_ASR_1D=0x1f

    # function alias
    LD_ReadReg = self.read
    LD_WriteReg = self.write
    delay = self.delay
    LD_Init_Common = self.commonInit

    # start init
    LD_ReadReg(0x06)  
    LD_WriteReg(0x17, 0x35) 
    delay(10)
    LD_ReadReg(0x06)  

    LD_WriteReg(0x89, 0x03)  
    delay(5)
    LD_WriteReg(0xCF, 0x43)   
    delay(5)
    LD_WriteReg(0xCB, 0x02)
    
    #/*PLL setting*/
    LD_WriteReg(0x11, LD_PLL_11)       
    if nLD_Mode == 'MODE_MP3':
      LD_WriteReg(0x1E, 0x00) 
      LD_WriteReg(0x19, LD_PLL_MP3_19)   
      LD_WriteReg(0x1B, LD_PLL_MP3_1B)   
      LD_WriteReg(0x1D, LD_PLL_MP3_1D)
    else:
      LD_WriteReg(0x1E,0x00)
      LD_WriteReg(0x19, LD_PLL_ASR_19) 
      LD_WriteReg(0x1B, LD_PLL_ASR_1B)   
      LD_WriteReg(0x1D, LD_PLL_ASR_1D)
    delay(10)
    LD_WriteReg(0xCD, 0x04)
    LD_WriteReg(0x17, 0x4c) 
    delay(5)
    LD_WriteReg(0xB9, 0x00)
    LD_WriteReg(0xCF, 0x4f) 
    print("Common init ok.")
    interruptType = self.read(0x2B)
    interruptEnable = self.read(0x29)
    fifoIntEnable = self.read(0x02)
    print("int-type:0x%x, int-enable:0x%x, fifoInt:0x%x"%(interruptType, interruptEnable, fifoIntEnable))

  def initMP3(self):
    # function alias
    LD_ReadReg = self.read
    LD_WriteReg = self.write
    delay = self.delay
    LD_Init_Common = self.commonInit

    LD_Init_Common('MODE_MP3')
    LD_WriteReg(0xBD,0x02)
    LD_WriteReg(0x17, 0x48)
    delay(10)
    LD_WriteReg(0x85, 0x52) 
    LD_WriteReg(0x8F, 0x00)  
    LD_WriteReg(0x81, 0x00)
    LD_WriteReg(0x83, 0x00)
    LD_WriteReg(0x8E, 0xff)
    LD_WriteReg(0x8D, 0xff)
    delay(1)
    LD_WriteReg(0x87, 0xff)
    LD_WriteReg(0x89, 0xff)
    delay(1)
    LD_WriteReg(0x22, 0x00)    
    LD_WriteReg(0x23, 0x00)
    LD_WriteReg(0x20, 0xef)    
    LD_WriteReg(0x21, 0x07)
    LD_WriteReg(0x24, 0x77)          
    LD_WriteReg(0x25, 0x03)
    LD_WriteReg(0x26, 0xbb)    
    LD_WriteReg(0x27, 0x01) 
    print("Init MP3 OK.")

  def initASR(self):
    # function alias
    LD_ReadReg = self.read
    LD_WriteReg = self.write
    delay = self.delay
    LD_Init_Common = self.commonInit

    LD_Init_Common('MODE_ASR')
    LD_WriteReg(0xBD, 0x00)
    LD_WriteReg(0x17, 0x48)
    delay( 10 )
    LD_WriteReg(0x3C, 0x80)    
    LD_WriteReg(0x3E, 0x07)
    LD_WriteReg(0x38, 0xff)    
    LD_WriteReg(0x3A, 0x07)
    LD_WriteReg(0x40, 0)          
    LD_WriteReg(0x42, 8)
    LD_WriteReg(0x44, 0)    
    LD_WriteReg(0x46, 8) 
    delay( 1 )
    print("Init ASR OK.")

  def isASRIdle(self):
    """ Is ASR DSP idle? True for idle."""
    flag = False
    for j in range(10):
      if self.read(0xb2) == 0x21:
        flag = True
        break
    self.delay(10)
    return flag
 
  def addKeyword(self, index, keyword):
    """ Add ASR keywords and index. 
        index: the id of a keyword
        keyword: the Pin Yin of a keyword, Chinese characters are seperated by spaces, max index is 255.
        return: True success, False fail when ASR DSP is busy.
    """
    if not self.isASRIdle():
      return False
    
    self.write(0xc1, index)
    self.write(0xc3, 0)
    self.write(0x08, 0x04)
    self.delay(1)
    self.write(0x08, 0x00)
    self.delay(1)
    for char in keyword:
      self.write(0x5, ord(char))
    self.write(0xb9, len(keyword))
    self.write(0xb2, 0xff)
    self.write(0x37, 0x04)
    return True

  def runASR(self):
    """ Start Auto Speech Recognize. 
        return: True for starting success, False for DSP busy.
    """
    MIC_VOL = 0x50 # ADC Gain, 0x00->0x7F, typical 0x40-0x6F
    self.write(0x35, MIC_VOL)
    self.write(0x1C, 0x09)
    self.write(0xBD, 0x20)
    self.write(0x08, 0x01)
    self.delay( 1 )
    self.write(0x08, 0x00)
    self.delay( 1 )
    if not self.isASRIdle():
      return False
    self.write(0xB2, 0xff)  
    self.write(0x37, 0x06)
    self.delay( 5 )
    self.write(0x1C, 0x0b)
    self.write(0x29, 0x10)
    self.write(0xBD, 0x00)
    return True

  def handleInterrupt(self):
    """ Handle interrupt.
      Return: (is found, index)
    """

    interruptType = self.read(0x2B)
    interruptEnable = self.read(0x29)
    fifoIntEnable = self.read(0x02)
    print("int-type:%s, int-enable:%s, fifoInt:%s"%(interruptType, interruptEnable, fifoIntEnable))
    self.write(0x29, 0) # disable all interrupt
    self.write(0x02, 0) # disable fifo interrupt
    if (interruptType & 0x10) and self.read(0xb2)==0x21 and self.read(0xbf)==0x35:
      nAsrResCount = self.read(0xba)
      if nAsrResCount > 0 and nAsrResCount < 4:
        found = True
      else:
        found = False
    else:
      found = False
    self.write(0x2B,0)
    self.write(0x1C,0)
    return (found,self.read(0xC5))

  @property
  def asrResult(self):
    intIndex = self.read(0x2b)
    print("intIndex: %s" % intIndex)
    return self.read(0xc5)

class LD3320_SPIDev:
  """The LD3320 driver implemented by spidev module."""

  def __init__(_self):
    import spidev
    dev = spidev.SpiDev()
    dev.open(0,0)
    dev.bits_per_word = 8
    dev.cshigh = False
    dev.loop = False
    dev.no_cs = False
    dev.lsbfirst = False
    dev.max_speed_hz = 7629
    dev.mode = 0b10
    dev.threewire = False
    _self.spi = dev

  def close(_self):
    if _self.spi:
      _self.spi.close()

  def reset(_self):
    pass

  def read(_self, reg):
    pass

  def write(_self, reg, data):
    pass

  def read_print(_self, reg):
    pass

  def test(self):
    self.reset()
    self.read(0x06)
    self.write(0x35,0x33)
    print("write 0x33")
    self.write(0x1b,0x55)
    print("write 0x55")
    self.write(0xb3,0xaa)
    print("write 0xaa")
    self.read_print(0x35)
    self.read_print(0x1b)
    self.read_print(0xb3)
    self.close()

