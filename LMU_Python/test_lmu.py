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

print(dir(cars))