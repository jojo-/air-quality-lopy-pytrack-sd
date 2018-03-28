import machine
import math
import network
import os
import time
import utime
from machine import RTC
from machine import SD
from machine import Timer
from L76GNSS import L76GNSS
from pytrack import Pytrack
import pycom
import struct
import gc

def sync_time_from_GPS(verbose=False):
    #Start GPS
    py = Pytrack()
    l76 = L76GNSS(py, timeout=600)
    #start rtc
    rtc = machine.RTC()
    if verbose:
        print('Aquiring GPS signal....')
    pycom.rgbled(0x7f0000)
    while (True):
       gps_datetime = l76.get_datetime()
       #case valid readings
       if gps_datetime[3]:
           day = int(gps_datetime[4][0] + gps_datetime[4][1] )
           month = int(gps_datetime[4][2] + gps_datetime[4][3] )
           year = int('20' + gps_datetime[4][4] + gps_datetime[4][5] )
           hour = int(gps_datetime[2][0] + gps_datetime[2][1] )
           minute = int(gps_datetime[2][2] + gps_datetime[2][3] )
           second = int(gps_datetime[2][4] + gps_datetime[2][5] )
           print("Current location: {}  {} ; Date: {}/{}/{} ; Time: {}:{}:{}".format(gps_datetime[0],gps_datetime[1], day, month, year, hour, minute, second))
           rtc.init( (year, month, day, hour, minute, second, 0, 0))
           break
    #Stop GPS
    set_LED_green()
    l76.stop(py)
    if verbose:
        print('RTC Set from GPS to UTC:', rtc.now())

def set_LED_green():
    pycom.rgbled(0x007f00)
    
def set_LED_red():
    pycom.rgbled(0x7f0000)
