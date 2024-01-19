# Code is written to be run on a Raspberry Pi
Check Kinéis KIM1 user manual.  
This code is based on KIM1 Firmware version **KIM1_V2.1**
For further assistance, feel free to contact Kinéis at the following link: https://www.kineis.com/contact/

# Run the example code:
`sudo python3 main.py`

# Configure RPi pins
`ON_OFF_KIM_PIN = 12`  
using GPIO18, Pin12

`SERIAL_PORT = "/dev/ttyS0"`  
using TX:GPIO14,Pin08 / RX:GPIO15,Pin10

# Other configurations
`KIMPI_DEBUG = 1`  
set to 0 to stop output printing

`set_PWR(pwr)`  
where `pwr` is one of 100, 250, 500, 750 or 1000

