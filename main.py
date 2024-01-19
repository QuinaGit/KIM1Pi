#!/usr/bin/python3
'''
Author: Quintin Strydom, 2024 Jan

Notes:  * Remember to enable Serial communication on the Pi
        * The RPi access to the UART ports are:
            - ttyAMA0 if using PL011
            - ttyS0   if using mini UART (recommended)
        * 

'''
from time import sleep
import KIMPi

# CONFIGURATION DEFAULTS
interval_secs = 3600
pwr = 100                                         # 100,250,500,750,1000(default)
data = "BB7572A3C6D5D417D61E148D29C3110860B2C050E672A3C6D5D417D61E148D"

try:
  print("Example KIM1 Pi shield")

  KIMPi.init()

  KIMPi.set_sleepmode(True)
  
  if(KIMPi.set_sleepmode(False)):
    raise RuntimeError("Wake up fail. Please check wiring and jumpers.")
  else:
    print(" -- Wake up success")

  print("---")

  print("KIM -- Set PWR : ",end='')
  KIMPi.set_PWR(pwr)

  print("KIM -- Get ID : ",end='')
  print(KIMPi.get_ID())

  print("KIM -- Get SN : ",end='')
  print(KIMPi.get_SN())

  print("KIM -- Get FW : ",end='')
  print(KIMPi.get_FW())

  print("KIM -- Get PWR : ",end='')
  print(KIMPi.get_PWR())

  print("KIM -- Get FRQ : ",end='')
  print(KIMPi.get_ATXFRQ())

  print("KIM -- Send data ... ")
  if(KIMPi.send_data(data)):
    print("Message sent")
  else:
    print("KIM -- Error: message not sent")

  print("KIM -- Turn OFF")

  KIMPi.set_sleepmode(True)
  sleep(interval_secs)
  KIMPi.set_sleepmode(False)

except Exception as err:
  print("ERROR: ",type(err).__name__, "–", err) 

finally:
  KIMPi.deinit()
