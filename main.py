# Air Quality Sensing
#
# Main script
# todo: filter data, add temperature, check calibration of co2 co2_sensor,
#       develop a proper PSU for the sensors, use external ADC board
#       calibrate ADC: https://docs.pycom.io/chapter/tutorials/all/adc.html
#       use adcchannel.voltage() method instead:
#           https://docs.pycom.io/chapter/firmwareapi/pycom/machine/ADC.html
#       wifi enabled for OTA firmware update

import time
import socket
import struct
import config
import gc
from machine import Pin, UART, SD, RTC, deepsleep
from L76GNSS import L76GNSS
from pytrack import Pytrack
import pycom

# mounting sd card
sd = SD()
os.mount(sd, '/sd')

# enabling garbage collector
gc.enable()

# init uart with the sensor on pins 10 and 11
uart1 = UART(1, baudrate=9600, timeout_chars=7, pins=('P10','P11'))

# init RTC
rtc = RTC()

# init SET pin of the sensors on pin 12
set_pin = Pin('P9', mode=Pin.OUT, pull=Pin.PULL_DOWN)
set_pin.value(0)

def read_pm():
    '''Reading the distance using the ultrasonic sensor via serial port '''

    # set the SET pin (activation pin) to 1
    set_pin.value(1)

    # wait 3 seconds to make sure that the buffer is filled
    time.sleep_ms(3000)
    raw_packet = uart1.readall()

    # set the SET pin to 0
    set_pin(0)

    # finding the start/end of the packet and extracting it
    idx_begin = raw_packet.find(b'B')
    idx_end   = idx_begin + 31
    packet = raw_packet[idx_begin:idx_end]

    # pm concentrations
    pm1_0 = int.from_bytes(packet[4:6], 'high')
    pm2_5 = int.from_bytes(packet[6:8], 'high')
    pm10  = int.from_bytes(packet[8:10], 'high')



    # return the concentrations
    return (pm1_0, pm2_5, pm10)


def sync_time_from_gps(timeout=60):

    # Getting the time from the GPS chip
    py = Pytrack()
    l76 = L76GNSS(py, timeout=timeout)
    if WAIT_FOR_GPS is True:
        while True:
            lat,lon= l76.coordinates(debug=True)
            if lat is None:
                print("no gps")
                pycom.rgbled(0xFFA500)
                time.sleep(5)
                pycom.rgbled(0x7f0000)
            else:
                pycom.rgbled(0x007f00)
                print(lat + " " + lon)
                break
    time_gps = l76.get_time(debug=True)
    hh = int(time_gps[:2])
    mm = int(time_gps[2:4])
    ss = int(time_gps[4:6])

    # init the rtc with a given timezone timezone
    rtc.init((2018,1,1,hh,mm,ss))
    time.timezone(config.TIMEZONE_OFFSET)

    # switch off the gps
    l76.stop(py)

    return(time_gps)

def write_to_file(pm1 = 0, pm2_5=0, pm10 = 0):

    # Opening the file in append mode
    f = open('/sd/data.csv', 'a')

    # Creating the data string, just keeping the dd:hh:mm:ss part of the time
    time_str = "{0}".format(time.localtime()[3:6])[1:-1]
    data = "{0},{1},{2},{3}".format(time_str, pm1, pm2_5, pm10)

    # Write and close the file
    f.write(data + "\n")
    f.close()

'''
################################################################################
#
# Main script
#
# 1. Read the time from the GPS
# 2. Read pm values
# 3. Save those values on the SD card
#
################################################################################
'''
if WAIT_FOR_GPS is True:
    pycom.rgbled(0x7f0000)
sync_time_from_gps(60)

while True:

    (pm1_0, pm2_5, pm10) = read_pm()
    print('pm1   =' + str(pm1_0) + ' ug/m3')
    print('pm2.5 =' + str(pm2_5) + ' ug/m3')
    print('pm10  =' + str(pm10) + ' ug/m3')

    write_to_file(pm1_0, pm2_5, pm10)

    gc.collect()
    time.sleep(config.INT_SAMPLING)

#deepsleep(config.INT_SAMPLING)
