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

def leaderboard():
    try:
        leaderboard = []

        for car in cars:
            name = bytes(car.mDriverName).decode('utf-8', errors='ignore').strip('\x00')
            place = car.mPlace
            category = bytes(car.mVehicleClass).split(b'\x00')[0].decode("utf-8", errors="ignore")
            vehicle = bytes(car.mVehicleName).split(b'\x00')[0].decode("utf-8", errors="ignore")
            laps = car.mTotalLaps
            behind = car.mTimeBehindLeader

            if name and place > 0:
                leaderboard.append({
                    "name": name,
                    "place": place,
                    "category": category,
                    "vehicle": vehicle,
                    "laps": laps,
                    "behind": behind
                })

        leaderboard.sort(key=lambda x: x["place"])

        for i, driver in enumerate(leaderboard):
            if i == 0:
                driver["interval"] = "-"
            else:
                diff = leaderboard[i]["behind"] - leaderboard[i - 1]["behind"]
                driver["interval"] = f"{round(diff, 1)}s" if diff >= 0 else "-"

        for driver in leaderboard:
            driver["behind"] = f"{round(driver['behind'], 1)}s"

        return leaderboard

    except Exception as e:
        return "Error"
    
print(leaderboard())