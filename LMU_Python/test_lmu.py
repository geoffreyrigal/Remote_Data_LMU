bib = ["sys", "time", "flask", "flask_cors", "math", "numpy", "threading", "requests", "psutil"]
import os
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

info = SimInfoAPI()
cars = info.Rf2Scor.mVehicles
t = info.playersVehicleTelemetry()
s = info.playersVehicleScoring()
e = info.Rf2Ext
scoring_info = info.Rf2Scor.mScoringInfo

