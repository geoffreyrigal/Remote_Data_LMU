import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
shared_memory_path = os.path.join(current_dir, "..", "pyRfactor2SharedMemory")
sys.path.append(shared_memory_path)
import time
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS
from sharedMemoryAPI import SimInfoAPI # type: ignore
import math
import numpy as np
import csv
import ctypes
import mmap
import struct
import subprocess
import threading
import requests

app = Flask(__name__)
CORS(app)
script_running = False
script_thread = None

info = SimInfoAPI()
cars = info.Rf2Scor.mVehicles
t = info.playersVehicleTelemetry()
s = info.playersVehicleScoring()
scoring_info = info.Rf2Scor.mScoringInfo

print(dir(cars))