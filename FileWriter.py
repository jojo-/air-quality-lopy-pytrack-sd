#from pytrack import Pytrack
from machine import SD
import os

class FileWriter(object):
    """docstring for [object Object]."""
    def __init__(self):
        sd = SD()
        os.mount(sd,'/sd')

    def _write(self, filepath,mode,data):
        f = open(filepath,mode)
        f.write(data + "\n")
        f.close()
