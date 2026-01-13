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

def get_wind_data():
    # Définition de la rose des vents (Tuple de limites)
    wind_rose_map = {
        (348.75, 11.25): "N",
        (11.25, 33.75): "NNE",
        (33.75, 56.25): "NE",
        (56.25, 78.75): "ENE",
        (78.75, 101.25): "E",
        (101.25, 123.75): "ESE",
        (123.75, 146.25): "SE",
        (146.25, 168.75): "SSE",
        (168.75, 191.25): "S",
        (191.25, 213.75): "SSW",
        (213.75, 236.25): "SW",
        (236.25, 258.75): "WSW",
        (258.75, 281.25): "W",
        (281.25, 303.75): "WNW",
        (303.75, 326.25): "NW",
        (326.25, 348.75): "NNW"
    }

    # Calcul de la vitesse (m/s) -> Conversion en km/h pour le dashboard
    raw_speed = math.sqrt((scoring_info.mWind.x**2) + (scoring_info.mWind.z**2))
    wind_speed_kmh = round(raw_speed * 3.6, 1)

    # Calcul de l'angle (0° = Nord, 90° = Est)
    wind_degres = (math.degrees(math.atan2(scoring_info.mWind.x, scoring_info.mWind.z)) + 360) % 360
    
    cardinal_result = "N" # Valeur par défaut

    # Parcours du dictionnaire
    for (d_min, d_max), name in wind_rose_map.items():
        if d_min > d_max:  # Cas spécial du passage par 0° (Nord)
            if wind_degres >= d_min or wind_degres < d_max:
                cardinal_result = name
                break
        else:
            if d_min <= wind_degres < d_max:
                cardinal_result = name
                break

    return {
        "speed": wind_speed_kmh,
        "degrees": round(wind_degres, 2),
        "direction": cardinal_result
    }

print(get_wind_data())