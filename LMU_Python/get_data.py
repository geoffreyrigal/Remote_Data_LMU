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

"""
Lancer LMU en essai pendant 4h avec une seule catégorie (hy, gt3, lmp2,...)
Ce programme doit écrire dans un csv les infos des differentes voitures à chaque fin de tour
"""

path = "C:\\Users\\geoff\\Desktop\\Informatique\\lmu\\LMU_Python"
os.chdir(path)
info = SimInfoAPI()
cars = info.Rf2Scor.mVehicles
t = info.playersVehicleTelemetry()
s = info.playersVehicleScoring()
scoring_info = info.Rf2Scor.mScoringInfo

print(dir(info))

def fahrenheit_to_celsius(f):
    return round((f - 32) * 5 / 9, 1)

def get_lap_number():
    return t.mLapNumber

best_lap = [math.inf]
def get_lap_time(): #Définis le best lap (ligne +5), retourne le temps du dernier tour et le delta avec le meilleur tour
    if get_lap_number != 0:
        lap_time = s.mLastLapTime
        delta_best_lap = best_lap[0] - lap_time
        if lap_time < best_lap[0]:
            best_lap[0] = lap_time
        return [lap_time, delta_best_lap]
    return ["N/A", "N/A"]

def get_front_tire_type():
    return bytes(getattr(t, "mFrontTireCompoundName", b"")).decode("utf-8", errors="ignore").strip("\x00")

def get_rear_tire_type():
    return bytes(getattr(t, "mRearTireCompoundName", b"")).decode("utf-8", errors="ignore").strip("\x00")

def get_tire_usage():
    ...

def get_tire_temp():
    return [
        fahrenheit_to_celsius((t.mWheels[0].mTemperature[0] + t.mWheels[0].mTemperature[1] + t.mWheels[0].mTemperature[2]) / 3),
        fahrenheit_to_celsius((t.mWheels[1].mTemperature[0] + t.mWheels[1].mTemperature[1] + t.mWheels[1].mTemperature[2]) / 3),
        fahrenheit_to_celsius((t.mWheels[2].mTemperature[0] + t.mWheels[2].mTemperature[1] + t.mWheels[2].mTemperature[2]) / 3),
        fahrenheit_to_celsius((t.mWheels[3].mTemperature[0] + t.mWheels[3].mTemperature[1] + t.mWheels[3].mTemperature[2]) / 3)
    ]

def get_fuel_level():
    return t.mFuel

def get_fuel_consomation():
    ...

def get_speed():
    vx, vy, vz = t.mLocalVel.x, t.mLocalVel.y, t.mLocalVel.z
    return round(math.sqrt(vx**2 + vy**2 + vz**2) * 3.6, 1)

def get_max_speed():
    ...

def get_avg_speed():
    ...

def get_car():
    return bytes(s.mVehicleName).split(b'\x00')[0].decode("utf-8", errors="ignore")

def get_category(): # Possible erreur sur cette fonction
    return bytes(cars[1].mVehicleClass).split(b'\x00')[0].decode("utf-8", errors="ignore")

def get_track():
    return bytes(bytearray(getattr(scoring_info, "mTrackName", b""))).split(b'\x00')[0].decode("utf-8", errors="ignore").strip('\x00')

def get_track_lenght():
    return scoring_info.mLapDist

if __name__ == "__main__":
    car_used = get_car()
    track_name = get_track()
    track_lenght = get_track_lenght()
    last_laps = {i: -1 for i in range(len(cars))}

    while True:
        info.update()  # met à jour les infos depuis le jeu
        for i, car in enumerate(cars):
            current_lap = car.mLapNumber

            # Si le numéro de tour a changé => fin d'un tour
            if current_lap != last_laps[i]:
                if last_laps[i] != -1:  # éviter de déclencher au tout début
                    #action
                    print(f"Voiture {i} a terminé le tour {current_lap}")
                last_laps[i] = current_lap

        time.sleep(0.1)