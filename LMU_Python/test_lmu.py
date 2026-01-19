import sys
sys.path.append(r"C:\Users\geoff\Desktop\Informatique\lmu\pyRfactor2SharedMemory")
import time
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS
from sharedMemoryAPI import SimInfoAPI # type: ignore
import math
import numpy as np
import csv
import os
import ctypes
import mmap
import struct
import subprocess
import threading
import requests

app = Flask(__name__)
CORS(app)
info = SimInfoAPI()
script_running = False
script_thread = None

cars = info.Rf2Scor.mVehicles
t = info.playersVehicleTelemetry()
s = info.playersVehicleScoring()
scoring_info = info.Rf2Scor.mScoringInfo
e = info.Rf2Ext


"""# Vérification dans le bloc étendu brut
import struct

# On accède au bloc mmap brut que vous avez trouvé
raw_data = info._rf2_ext

# On lit 1 octet (c_byte) à l'index 1084 (Offset pour mInCarTC)
in_car_tc = struct.unpack('b', raw_data[1084:1085])[0]

# On lit 1 octet à l'index 1085 (Offset pour mInCarABS)
in_car_abs = struct.unpack('b', raw_data[1085:1086])[0]

print(f"TC Voiture (Brut) : {in_car_tc}")
print(f"ABS Voiture (Brut) : {in_car_abs}")"""

print(t.mWheels[0].mLateralForce)