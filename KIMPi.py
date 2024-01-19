'''
Author: Quintin Strydom
Created: January 2024
For use of Raspberry Pi

Typical responses from KIM1:
  * +SN=KIM12345678900
  * +ID=123456b
  * +FW=KIM1_V2.1
  * +ATXFRQ=401650000
  * +PWR=1000
  * +AFMT=0,0,0
  * +OK
'''

# -------------------------------------------------------------------------- //
#! IMPORTS
# -------------------------------------------------------------------------- //
import serial
import RPi.GPIO as GPIO
from time import sleep

# -------------------------------------------------------------------------- //
#! GLOBAL VARIABLES
# -------------------------------------------------------------------------- //
KIMPI_DEBUG = 1                                   # set to 0 to stop output printing
ser = None
pinON_OFF_used = True
response = None

ON_OFF_KIM_PIN = 12                               # GPIO18, Pin12
BAUDRATE = 9600
SERIAL_PORT = "/dev/ttyS0"                        # TX:GPIO14,Pin08 / RX:GPIO15,Pin10

# CONSTANTS
AT_PING    = 'AT+PING=?'
AT_ID      = 'AT+ID='
AT_SN      = 'AT+SN='
AT_FW      = 'AT+FW='
AT_ATXFRQ  = 'AT+ATXFRQ='
AT_PWR     = 'AT+PWR='
AT_AFMT    = 'AT+AFMT='
AT_CW      = 'AT+CW='
AT_TX      = 'AT+TX='
AT_SAVE_CFG= 'AT+SAVE_CFG'
AT_REQUEST = '?'

# KIM1 RETURN VALUES
OK_KIM            = 0,                            # OK return by KIM
ERROR_KIM         = 1,                            # Error returned by KIM
UNKNOWN_ERROR_KIM = 2,                            # Something unknown returned by KIM
TIMEOUT_KIM   	  = 3                             # Timeout, nothing returned by KIM

# -------------------------------------------------------------------------- //
#! debug print - set KIMPI_DEBUG to enable print
# -------------------------------------------------------------------------- //
def DBprint(msg,*args,**kwargs):
  if KIMPI_DEBUG:
    print(msg,*args,**kwargs)

# -------------------------------------------------------------------------- //
#! init functions
# -------------------------------------------------------------------------- //
def init_serial():
  global ser,BAUDRATE,SERIAL_PORT
  ser = serial.Serial(SERIAL_PORT,BAUDRATE,timeout=1)

def init():
  DBprint("INFO: initialise")
  global pinON_OFF_used
  init_serial()
  if pinON_OFF_used:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ON_OFF_KIM_PIN,GPIO.OUT)
    GPIO.output(ON_OFF_KIM_PIN,False)
    DBprint("INFO: Serial and GPIO initialised")
  else:
    DBprint("INFO: Serial initialised")

# -------------------------------------------------------------------------- //
#! destructor functions must be called at the end
# -------------------------------------------------------------------------- //
def deinit_serial():
  global ser 
  ser.__del__()				                            # De-initialise and close port

def deinit():
  DBprint("INFO: KIMpi - Clean up") 
  deinit_serial()
  GPIO.cleanup()                                  # cleanup all GPIO 

# -------------------------------------------------------------------------- //
#! Get the status of the KIM1 module : ON or OFF
# -------------------------------------------------------------------------- //
def get_sleepmode() -> bool:
  global pinON_OFF_used
  if(pinON_OFF_used == True):
    if (GPIO.input(ON_OFF_KIM_PIN) == True):
      return False
    else:
      return True
  else:
    return False

# -------------------------------------------------------------------------- //
#! Set the status of the KIM1 module : ON or OFF - return new sleepmode state
# -------------------------------------------------------------------------- //
def set_sleepmode(mode: bool) -> bool:
  global ser
  global pinON_OFF_used

  if (pinON_OFF_used):

    if (get_sleepmode() == mode):
      return True
    
    else:
      if (mode == False):
        init_serial()
        ser.reset_output_buffer() 		            # clean TX buffer
        ser.reset_input_buffer() 		              # clean RX buffer
        
        GPIO.output(ON_OFF_KIM_PIN,True) 	        # when State_pin is put HIGH, KIM sends SN packet (NOPE)
        sleep(0.02)                               # required after ON-OFF pin pulled HIGH for serial line to init

        if send_PING():
          return False                            # ping successfull
        else:
          DBprint("ERROR: Ping not received") # todo: maybe raise exeption??
          return True

      else: #mode == True
        GPIO.output(ON_OFF_KIM_PIN,False)
        ser.reset_output_buffer() 		            # clean TX buffer
        ser.reset_input_buffer() 		              # clean RX buffer
        deinit_serial()
        return True

  else:
    if (mode == True):
      return False
    else:
      return True

# -------------------------------------------------------------------------- //
#! Send AT command to the KIM module.
# -------------------------------------------------------------------------- //
def send_ATcommand(command):
  global ser
  global response
    
  ser.reset_output_buffer() 	                    # clean TX buffer
  ser.reset_input_buffer() 		                    # clean RX buffer

  response = None
  serBuff = None
  ser.write((command+'\r\n').encode('utf-8'))     # send command with <CR><LF>

  for i in range(10):

    serBuff = ser.readline(20)
    DBprint("INFO: Command = `"+command+" - Response = ",serBuff)

    if serBuff == None or len(serBuff) <= 1: 
      serBuff = None
      continue 

    response = serBuff.decode('utf-8')

    if (response[2] == 'X'):
      return 0 # OK_KIM -> +TX=0,<data>

    if (response[1] == 'O' or                     # +OK	
        response[1] == 'I' or                     # +ID=
        response[1] == 'S' or                     # +SN=
        response[1] == 'F' or                     # +FW=
        response[2] == 'T' or                     # +ATXFRQ=
        response[1] == 'P' or                     # +PWR=
        response[2] == 'F' or                     # +AFMT=
      # response[1] == 'C' or                     # +CW=OK
        response[2] == 'X'                        # +TX=0,<data>
    ):
      if (command[4] != 'X'):                     # AT+TX=
        return 0 # OK_KIM
      else:
        return 2 # UNKNOWN_ERROR_KIM
      
    elif (response[1] == 'R'):  # ERROR=
        return 1 # ERROR_KIM
  
  return 3 # TIMEOUT_KIM

# Responses - Error todo:
# * errno
# * • 1: Unknow error
# * • 2: format of parameter is incorrect
# * • 3: parameters are missing
# * • 4: too many parameters
# * • 5: the value of the parameter is incompatible
# * • 6: the AT command is unknown
# * • In case of any other value, please reach out to Kinéis technical support

# --------------------------------------------------------------------------
#! Get the ID of the KIM1 module.
# --------------------------------------------------------------------------
def get_ID():
  global response
  global AT_ID,AT_REQUEST
  send_ATcommand(AT_ID + AT_REQUEST)
  return response

# -------------------------------------------------------------------------- //
#! Get the Serial Number of the KIM1 module.
# -------------------------------------------------------------------------- //
def get_SN():
  global response
  global AT_SN,AT_REQUEST
  send_ATcommand(AT_SN + AT_REQUEST)
  return response

# -------------------------------------------------------------------------- //
#! Get the Firmware Version of the KIM1 module.
# -------------------------------------------------------------------------- //
def get_FW():
  global response
  global AT_FW,AT_REQUEST
  send_ATcommand(AT_FW + AT_REQUEST)
  return response

# -------------------------------------------------------------------------- //
#! Get the frequency offset of the KIM1 module.
# -------------------------------------------------------------------------- //
def get_ATXFRQ():
  global response
  global AT_ATXFRQ,AT_REQUEST
  send_ATcommand(AT_ATXFRQ + AT_REQUEST)
  return response

# -------------------------------------------------------------------------- //
#! Get the transmit power of the KIM1 module.
# -------------------------------------------------------------------------- //
def get_PWR():
  global response
  global AT_PWR,AT_REQUEST
  send_ATcommand(AT_PWR + AT_REQUEST)
  return response

# -------------------------------------------------------------------------- //
#! Get the selected message format
# -------------------------------------------------------------------------- //
def get_AFMT():
  global response
  global AT_AFMT,AT_REQUEST
  send_ATcommand(AT_AFMT + AT_REQUEST)
  return response

# -------------------------------------------------------------------------- //
#! Set the transmit power of the KIM1 module. 
# -> AT+PWR =<pwr>
#   * <pwr>= 100,250,500,750,1000(default)
# -------------------------------------------------------------------------- //
def set_PWR(pwr:int) -> bool:
  global AT_PWR
  if send_ATcommand(AT_PWR + str(pwr)) == 0:
    return True
  return False

# -------------------------------------------------------------------------- //
#! Set the message format. 
# -> AT+AFMT=<fmt>[,<crc>,<bch>]
#   * <fmt> - an integer to select the message format 0:raw,1_Keneis standard
#   * <crc> - length of the CRC 0,16
#   * <bch> - length of the BCH 0,32
# -------------------------------------------------------------------------- //
def set_AFMT(fmt:str,crc:str=None,bch:str=None) -> bool:
  global AT_AFMT
  if crc == None or bch == None:
    if send_ATcommand(AT_AFMT + fmt) == 0:
      return True
  else:
    if send_ATcommand(AT_AFMT + fmt +','+ crc +','+ bch) == 0:
      return True
  return False

# -------------------------------------------------------------------------- //
#! Save configuration
# -------------------------------------------------------------------------- //
def send_SAVE_CFG() -> bool:
  if send_ATcommand(AT_SAVE_CFG) == 0:
    return True
  return False

# -------------------------------------------------------------------------- //
#! Ping Communication test
# -------------------------------------------------------------------------- //
def send_PING() -> bool:
  global AT_PING
  if send_ATcommand(AT_PING) == 0:
    return True
  return False

# -------------------------------------------------------------------------- //
#! Send data to satellites
# -------------------------------------------------------------------------- //
def send_data(data:str) -> bool:
  global AT_TX
  # todo: check the maximum length ()
  if send_ATcommand(AT_TX + data) == 0:
    return True
  return False

# -------------------------------------------------------------------------- //
#! Generate Carrier Wave signal - duration,frq,pwr - only for testing
# -> AT+CW=<duration>[,<frq>[,<pwr]]
#   * <duration> - duration of the CW, in steps of 100 milliseconds 
#                                         (max:3000=300seconds)
#   * <frq> - frequency of the CW signal, in Hz
#   * <pwr> - transmission power of the CW signal
# -------------------------------------------------------------------------- //
def send_CW(duration:int,frq:int=None,pwr:int=None) -> bool:
  global AT_CW
  command = AT_AFMT + str(duration)
  if pwr == None:
    if frq == None:
      if send_ATcommand(command) == 0:
        return True
    else:
      if send_ATcommand(command +','+ str(frq)) == 0:
        return True
  else:
    if frq != None:
      if send_ATcommand(command +','+ str(frq) +','+ str(pwr)) == 0:
        return True
  return False
