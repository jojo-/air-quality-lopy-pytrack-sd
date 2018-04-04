## Test code for read date/time from gps and update RTC
from pytrack import Pytrack
import SMARTools
import config
from SEN0177 import SEN0177
import machine
from FileWriter import FileWriter
import time
# setup as a station

import gc
try:
    time.sleep(2)
    gc.enable()

#Synchronize the board with GPS Time (!bloking!)
    SMARTools.sync_time_from_GPS(verbose=True)

#Init the SEN0177 Sensor
    sen0177 = SEN0177(PTX='P10',PRX='P11',PSLEEP='P9')

#Init FileWriter
    filewriter = FileWriter()

    while True:
    #Read sensor data
        (pm1_0,pm2_5,pm10)= sen0177._read_PM()
        time_str = "{0}".format(time.localtime()[3:6])[1:-1]
        data = "{0},{1},{2},{3}".format(time_str, pm1_0, pm2_5, pm10)
        print('pm1   =' + str(pm1_0) + ' ug/m3')
        print('pm2.5 =' + str(pm2_5) + ' ug/m3')
        print('pm10  =' + str(pm10) + ' ug/m3')
        print(data)

        filewriter._write(config.FILE_PATH,config.FILE_MODE,data)

        gc.collect()
        time.sleep(config.INT_SAMPLING)
except:
    print("Oups, something went wrong....")
    SMARTools.sed_LED_purple()
    machine.reset()
