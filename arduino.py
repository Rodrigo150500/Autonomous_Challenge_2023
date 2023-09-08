from pyfirmata import Arduino, util
import time

Uno = Arduino('COM3')



while True:
    Uno.digital[13].write(1)
    time.sleep(0.1)
    Uno.digital[13].write(0)
    time.sleep(0.1)
