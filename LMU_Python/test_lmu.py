bib = ["sys", "time", "flask", "flask_cors", "math", "numpy", "threading", "requests", "psutil"]
try:
    import os
    import subprocess
except ImportWarning:
    print("Veuillez installer la bib 'os' et/ou 'subprocess' ==> pip install os/subprocess")

import sys
project_path = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(f"{project_path}\\..\\pyRfactor2SharedMemory")
import time
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS
from sharedMemoryAPI import SimInfoAPI # type: ignore
import math
import numpy as np
import os
import threading
import requests

os.chdir(project_path)
API_KEY = "c21f29f8-5d60-44dc-920a-984bee09df9a"
DEVICE = "08:03:D0:C9:07:0C:1F:BE"
BASE_URL = "https://developer-api.govee.com/v1"
MODEL = "H6008"
HEADERS = {
    "Govee-API-Key": API_KEY,
    "Content-Type": "application/json"
}

app = Flask(__name__, static_folder="static")
CORS(app)
script_running = False
script_thread = None

################################# Global Variables #################################
info = SimInfoAPI()
cars = info.Rf2Scor.mVehicles
t = info.playersVehicleTelemetry()
s = info.playersVehicleScoring()
e = info.Rf2Ext
scoring_info = info.Rf2Scor.mScoringInfo


classements = ["GT3", "LMP3", "LMP2", "Hyper"]
error_code = [
    "Plugins not connected",
    "Too many Govee requests",
    "Uknown flag",
    "Error during getting data"
    ]

current_flag = ""
previous_flag = ""

while True:
    # 1. On récupère la télémétrie fraîche
    t = info.playersVehicleTelemetry()
    
    # 2. On esquive le blocage des développeurs en utilisant les forces G du châssis !
    vehicle_forces = {
        "lateral_G_force": t.mLocalAccel.x,     # Force dans les virages
        "longitudinal_G_force": t.mLocalAccel.z # Force au freinage et à l'accélération
    }

    print(vehicle_forces)
    time.sleep(1)