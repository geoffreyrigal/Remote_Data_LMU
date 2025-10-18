bib = ["sys", "time", "flask", "flask_cors", "math", "numpy", "threading", "requests", "psutil"]
try:
    import os
except ImportWarning:
    print("Veuillez installer la bib 'os' ==> pip install os")

for elem in bib:
    try:
        __import__(elem)
        print(f"{elem} est installé avec succès")
    except ImportError:
        choix = str(input(f"{elem}, n'est pas installé sur la machine. Souhaitez vous l'installer ? Y/N"))
        if choix == "Y" or choix == "y":
            os.system(f"pip install {elem}")
        elif choix == "N" or choix == "n":
            print("Le programme est fortement suceptible de ne pas marcher")
        else:
            print("Réponse invalide, veuillez recommencer.")
            exit()

import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
shared_memory_path = os.path.join(current_dir, "..", "pyRfactor2SharedMemory")
sys.path.append(shared_memory_path)
import time
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_cors import CORS
from sharedMemoryAPI import SimInfoAPI # type: ignore
import math
import numpy as np
import os
import threading
import requests

os.chdir(current_dir)
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
scoring_info = info.Rf2Scor.mScoringInfo

################################# Simple Function #################################

def send_command(name, value):
    payload = {
        "device": DEVICE,
        "model": MODEL,
        "cmd": {
            "name": name,
            "value": value
        }
    }
    response = requests.put(f"{BASE_URL}/devices/control", json=payload, headers=HEADERS)
    return response.status_code, response.text

def power(on: bool):
    return send_command("turn", "on" if on else "off")

def set_color(r: int, g: int, b: int):
    return send_command("color", {"r": r, "g": g, "b": b})

def set_brightness(level: int):
    return send_command("brightness", level)

def get_speed():
    vx, vy, vz = t.mLocalVel.x, t.mLocalVel.y, t.mLocalVel.z
    return round(math.sqrt(vx**2 + vy**2 + vz**2) * 3.6, 1)

def fahrenheit_to_celsius(f):
    return round((f - 32) * 5 / 9, 1)

def get_session():
    current_session = scoring_info.mSession
    if current_session > 0 and current_session < 5:
        return "Practice"
    elif current_session > 4 and current_session < 9:
        return "Qualification"
    elif current_session == 9:
        return "Warmup"
    elif current_session > 9 and current_session < 14:
        return "Race"
    else:
        return "N/A"

classements = ["GT3", "GTE", "LMP3", "LMP2", "LMP2_ELMS", "Hyper"]
def is_superior_class(my_class, other_class):
    try:
        my_rank = classements.index(my_class)
        other_rank = classements.index(other_class)
        return other_rank >= my_rank
    except ValueError:
        return False

current_flag = ""
previous_flag = ""
power(True)
def get_flag():
    global current_flag, previous_flag
    if scoring_info.mGamePhase == 0:
        current_flag = "Waiting..."
        if not current_flag == previous_flag:
            status, text = set_color(255, 0, 255)
            if status == 421:
                print("TOO MANY GOVEE API REQUESTS") 
            previous_flag = current_flag
        return current_flag
    
    elif s.mFinishStatus == 3:
        current_flag = "DSQ"
        if not current_flag == previous_flag:
            status, text = set_color(255, 255, 255)
            time.sleep(1)
            status, text = set_color(0, 0, 0)
            if status == 421:
                print("TOO MANY GOVEE API REQUESTS") 
            previous_flag = current_flag
        return current_flag

    elif s.mFlag == 0:
        current_flag = "GREEN"
        if not current_flag == previous_flag:
            status, text = set_color(0, 255, 0)
            if status == 421:
                print("TOO MANY GOVEE API REQUESTS") 
            previous_flag = current_flag
        return current_flag
        
    elif s.mFlag == 6:
        current_flag = "BLUE"
        if not current_flag == previous_flag:
            status, text = set_color(0, 0, 255)
            if status == 421:
                print("TOO MANY GOVEE API REQUESTS") 
            previous_flag = current_flag
        return current_flag
        
    elif scoring_info.mGamePhase == 7:
        current_flag = "FYC"
        if not current_flag == previous_flag:
            status, text = set_color(255, 255, 0)
            if status == 421:
                print("TOO MANY GOVEE API REQUESTS") 
            previous_flag = current_flag
        return current_flag

    else:
        if not current_flag == previous_flag:
            current_flag = s.mFlag
            print("ICIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII", current_flag)
            previous_flag = current_flag
        return current_flag

################################# All Pages #################################

@app.route("/warn_car_behind")
def isCarBehind(track_length=scoring_info.mLapDist):
    if not info.isRF2running() or not info.isSharedMemoryAvailable():
        return jsonify({"status": "not ready"})
    
    my_dist = s.mLapDist
    my_class = bytes(s.mVehicleClass).split(b'\x00')[0].decode("utf-8", errors="ignore")
    max_dist = float("inf")
    veih_clother = ""
    cat_clother = ""
    nbr_veih = 0
    
    for i in range(scoring_info.mNumVehicles):
        if i == s.mPlace:
            continue
        other = cars[i]
        if other.mIsPlayer == 0:
            other_class = bytes(other.mVehicleClass).split(b'\x00')[0].decode("utf-8", errors="ignore")
            if not is_superior_class(my_class, other_class) or my_class == other_class:
                continue
            if track_length == 0.0:
                return jsonify ({"warn": "False"})
            dist = (my_dist - other.mLapDist + track_length) % track_length
            if 0 < dist < 300 and dist < max_dist:
                veih_clother = bytes(other.mVehicleName).split(b'\x00')[0].decode("utf-8", errors="ignore")
                max_dist = dist
                cat_clother = other_class
                nbr_veih += 1
    
    if max_dist == float("inf"):
        return jsonify ({"warn": "False"})
    else:
        return jsonify ({
            "warn": "True",
            "veih_clother": veih_clother,
            "max_dist": max_dist,
            "cat_clother": cat_clother,
            "nbr_veih": nbr_veih
        })

@app.route("/warn_car_in_front")
def isCarInFront(track_length=scoring_info.mLapDist):
    if not info.isRF2running() or not info.isSharedMemoryAvailable():
        return jsonify({"status": "not ready"})
    
    my_dist = s.mLapDist
    my_class = bytes(s.mVehicleClass).split(b'\x00')[0].decode("utf-8", errors="ignore")
    max_dist = float("inf")
    veih_clother = ""
    cat_clother = ""
    nbr_veih = 0
    
    for i in range(scoring_info.mNumVehicles):
        if i == s.mPlace:
            continue
        other = cars[i]
        if other.mIsPlayer == 0:
            other_class = bytes(other.mVehicleClass).split(b'\x00')[0].decode("utf-8", errors="ignore")
            if is_superior_class(my_class, other_class) or my_class == other_class:
                continue
            if track_length == 0.0:
                return jsonify ({"warn": "False"})
            dist = (other.mLapDist - my_dist + track_length) % track_length
            if 0 < dist < 300 and dist < max_dist:
                veih_clother = bytes(other.mVehicleName).split(b'\x00')[0].decode("utf-8", errors="ignore")
                max_dist = dist
                cat_clother = other_class
                nbr_veih += 1
    
    if max_dist == float("inf"):
        return jsonify ({
            "warn": "False"
        })
    else:
        return jsonify ({
            "warn": "True",
            "veih_clother": veih_clother,
            "max_dist": max_dist,
            "cat_clother": cat_clother,
            "nbr_veih": nbr_veih
        })
    
@app.route("/flags")
def typeOfFlags():
    if not info.isRF2running() or not info.isSharedMemoryAvailable():
        return jsonify({"status": "not ready"})
    
    return jsonify ({
        "flag": get_flag(),
    })
    

################################# Practice Session #################################

avg_temp_tire = []
prog1_result = []

def tire_data_calculated(avg_temp_tire):
            #Max temp on every tire
    max_list_temp = [0, 0, 0, 0]
    for tick in avg_temp_tire:
        for tire in range (4):
            if tick[tire] > max_list_temp[tire]:
                max_list_temp[tire] = tick[tire]

            #Min temp on every tire
    min_list_temp = [float("inf"), float("inf"), float("inf"), float("inf")]
    for tick in avg_temp_tire:
        for tire in range (4):
            if tick[tire] < min_list_temp[tire]:
                min_list_temp[tire] = tick[tire]
                
            #Average temp on lap
    avg_list_temp = [0, 0, 0, 0]
    for tire in range (4):
        current_tire_temp_added = 0
        for tick in avg_temp_tire:
            current_tire_temp_added += tick[tire]
        avg_list_temp[tire] = current_tire_temp_added / len(avg_list_temp)
    
    return[avg_list_temp, max_list_temp, min_list_temp]
    

first_measured_lap_done = False
initial_lap = None

def prog1():
    global first_lap, initial_lap, initial_fuel, initial_tire_usage, avg_temp_tire, prog1_result, first_measured_lap_done

    current_lap = getattr(t, "mLapNumber", 0)

    if initial_lap is None:
        initial_lap = current_lap
        first_lap = True
        return

    # Si on a changé de tour
    if current_lap > initial_lap:
        print("FLAG NEW LAP 1")
        print(f"Nouveau tour détecté : {current_lap}")

        # S’exécute uniquement à la fin du tout premier tour de mesure
        if not first_lap and not first_measured_lap_done:
            print("FLAG NEW LAP 2")
            tire_usage = [initial_tire_usage[i] - t.mWheels[i].mWear for i in range(4)]
            lap_time = round(getattr(s, "mLastLapTime", 0.0), 3)
            fuel_used = initial_fuel - round(getattr(t, "mFuel", 0), 1)
            tire_info_in_lap = tire_data_calculated(avg_temp_tire)

            prog1_result.append([current_lap, lap_time, fuel_used, tire_usage, tire_info_in_lap])
            first_measured_lap_done = True
            avg_temp_tire.clear()

        first_lap = False
        initial_lap = current_lap
        initial_fuel = round(getattr(t, "mFuel", 0), 1)
        initial_tire_usage = [t.mWheels[i].mWear for i in range(4)]

        print("===========================================================")
        print(prog1_result)
        print("===========================================================")
        
    if not first_lap: #Pour ajouter les valeurs pendant le tour
        avg_temp_tire.append([
            fahrenheit_to_celsius(sum(t.mWheels[0].mTemperature) / 3),
            fahrenheit_to_celsius(sum(t.mWheels[1].mTemperature) / 3),
            fahrenheit_to_celsius(sum(t.mWheels[2].mTemperature) / 3),
            fahrenheit_to_celsius(sum(t.mWheels[3].mTemperature) / 3)
        ])

def prog2():
    ...

def prog3():
    ...

def run_script():
    global script_running, active_program
    active_program = int(active_program)
    while script_running:
        if active_program == 1:
            prog1()
        elif active_program == 2:
            prog2()
        elif active_program == 3:
            prog3()
        else:
            print("AY OUNE PROBLEM ICI (fonction 'run_script')")

@app.route("/status")
def get_status():
    global script_running, active_program
    return jsonify({
        "running": script_running,
        "program": active_program if script_running else None
    })

@app.route("/toggle")
def toggle_script():
    global script_running, script_thread, active_program
    program = request.args.get("program", "1")

    if not script_running:
        script_running = True
        active_program = program
        script_thread = threading.Thread(target=run_script)
        script_thread.start()
        return f"🟢 Programme {program} lancé"
    else:
        script_running = False
        active_program = None
        return f"🔴 Programme {program} stoppé"
"""
@app.route("/practice")
def practice_data():
    if not info.isRF2running() or not info.isSharedMemoryAvailable():
        return jsonify({"status": "not ready"})
    return jsonify({
        "lap": getattr(t, "mLapNumber", 0),
        "timeLap": round(getattr(s, "mLastLapTime", 0.0), 3),
        "fuel": round(getattr(t, "mFuel", 0), 1),
        "tireTemp_FL": fahrenheit_to_celsius((t.mWheels[0].mTemperature[0] + t.mWheels[0].mTemperature[1] + t.mWheels[0].mTemperature[2]) / 3),
        "tireTemp_FR": fahrenheit_to_celsius((t.mWheels[1].mTemperature[0] + t.mWheels[1].mTemperature[1] + t.mWheels[1].mTemperature[2]) / 3),
        "tireTemp_RL": fahrenheit_to_celsius((t.mWheels[2].mTemperature[0] + t.mWheels[2].mTemperature[1] + t.mWheels[2].mTemperature[2]) / 3),
        "tireTemp_RR": fahrenheit_to_celsius((t.mWheels[3].mTemperature[0] + t.mWheels[3].mTemperature[1] + t.mWheels[3].mTemperature[2]) / 3),
        "tireWear_FL": t.mWheels[0].mWear,
        "tireWear_FR": t.mWheels[1].mWear,
        "tireWear_RL": t.mWheels[2].mWear,
        "tireWear_RR": t.mWheels[3].mWear,
        "battery": round(battery, 2),
        "isPractice": get_session()
    })"""


################################# Global Page #################################
@app.route("/basic_race_info")
def basic_race_status():
    if not info.isRF2running() or not info.isSharedMemoryAvailable():
        return jsonify({"status": "not ready"})
    
    return jsonify({
        "sessionType": get_session(),
        "trackName": bytes(bytearray(getattr(scoring_info, "mTrackName", b""))).split(b'\x00')[0].decode("utf-8", errors="ignore").strip('\x00') if get_session() != "N/A" else "N/A",
        "vehicleName": bytes(s.mVehicleName).split(b'\x00')[0].decode("utf-8", errors="ignore") if get_session() != "N/A" else "N/A",
        "driverName": bytes(bytearray(getattr(scoring_info, "mPlayerName", b""))).split(b'\x00')[0].decode("utf-8", errors="ignore").strip('\x00') if get_session() != "N/A" else "N/A"
    })

@app.route("/race_status")
def race_status():
    if not info.isRF2running() or not info.isSharedMemoryAvailable():
        return jsonify({"status": "not ready"})
    
    return jsonify({
        "lap": getattr(t, "mLapNumber", 0),
        "total_laps": getattr(s, "mTotalLaps", 0),
        "position": getattr(s, "mPlace", 0),
        "best_lap": round(getattr(s, "mBestLapTime", 0),3) if getattr(t, "mLapNumber", 0) > 1 else "-",
        "last_lap": round(getattr(s, "mLastLapTime", 0),3) if getattr(t, "mLapNumber", 0) > 1 else "-",
        "delta_last_lap": round(getattr(s, "mLastLapTime", 0) - getattr(s, "mBestLapTime", 0),3) if getattr(t, "mLapNumber", 0) > 1 else "-",
    })

@app.route("/sector_times")
def sector_times():
    s1 = getattr(s, "mCurSector1", 0) if getattr(s, "mCurSector1", 0) > 0 else "-"
    s2 = getattr(s, "mCurSector2", 0) if getattr(s, "mCurSector2", 0) > 0 else "-"
    s3 = getattr(s, "mCurSector3", 0) if getattr(s, "mCurSector3", 0) > 0 else "-"

    best_s1 = getattr(s, "mBestSector1", 0)
    best_s2 = getattr(s, "mBestSector2", 0)
    best_s3 = getattr(s, "mBestLapTime", 0) - (best_s1 + best_s2)

    return jsonify({
        "sector1": s1,
        "sector2": s2,
        "sector3": s3,
        "best_sector1": best_s1,
        "best_sector2": best_s2,
        "best_sector3": best_s3
    })


@app.route("/leaderboard")
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

        return jsonify(leaderboard)

    except Exception as e:
        return jsonify({"error": str(e)})

################################# Car Data #################################
fuel_used_every_lap = []

current_lap = getattr(t, "mLapNumber", 0)
first_lap_while_program_running = getattr(t, "mLapNumber", 0)
fuel_level_at_begining = 0

def fuel_per_lap():
    global current_lap, fuel_level_at_begining, fuel_used_every_lap, t, first_lap_while_program_running
    lap_now = getattr(t, "mLapNumber", 0)

    if lap_now <= first_lap_while_program_running:
        fuel_level_at_begining = round(getattr(t, "mFuel", 0), 1)
        current_lap = lap_now
        return ["Unknown", "Unknown", "Unknown"]

    if lap_now != current_lap:
        fuel_level_at_end = round(getattr(t, "mFuel", 0), 1)
        fuel_used_for_this_lap = fuel_level_at_begining - fuel_level_at_end

        if current_lap > first_lap_while_program_running:
            fuel_used_every_lap.append(fuel_used_for_this_lap)

        fuel_level_at_begining = fuel_level_at_end
        current_lap = lap_now

    if fuel_used_every_lap:
        last = fuel_used_every_lap[-1]
        avg = np.mean(fuel_used_every_lap)
        fuel_now = round(getattr(t, "mFuel", 0), 1)
        return [f"{last:.2f}L", f"{avg:.2f}L", f"{fuel_now / avg:.2f}"]
    else:
        return ["Unknown", "Unknown", "Unknown"]

@app.route("/car_infos")
def car_infos():
    if not info.isRF2running() or not info.isSharedMemoryAvailable():
        return jsonify({"status": "not ready"})

    return jsonify({
        "speed": get_speed(),
        "rpm": round(getattr(t, "mEngineRPM", 0), 0),
        "gear": getattr(t, "mGear", 0),
        "fuel": round(getattr(t, "mFuel", 0), 1),
        "headlights": getattr(t, "mHeadlights", 0),
        "speedLimiterAvailable": "True" if getattr(t, "mSpeedLimiterAvailable", 0) == 1 else "false",
        "speedLimiter": "On" if getattr(t, "mSpeedLimiter", 0) == 1 else "Off",
        "frontTireName": bytes(getattr(t, "mFrontTireCompoundName", b"")).decode("utf-8", errors="ignore").strip("\x00"),
        "rearTireName": bytes(getattr(t, "mRearTireCompoundName", b"")).decode("utf-8", errors="ignore").strip("\x00"),
        "rearBreakBias": round(getattr(t, "mRearBrakeBias", 0)*100,2),
    })

@app.route("/car_data")
def car_data():
    if not info.isRF2running() or not info.isSharedMemoryAvailable():
        return jsonify({"status": "not ready"})
    
    def overheating():
        if getattr(t, "mOverheating", 0) == 0:
            return "False"
        else:
            return "True"
        
    
    damage_raw = getattr(t, "mDentSeverity", [0]*8)
    damage_list = list(damage_raw)
    
    return jsonify({
        "F": damage_list[0],
        "FL": damage_list[1],
        "CL": damage_list[2],
        "BL": damage_list[3],
        "R": damage_list[4],
        "BR": damage_list[5],
        "CR": damage_list[6],
        "FR": damage_list[7],
        "oilTemp": round(getattr(t, "mEngineOilTemp", 0),1),
        "waterTemp": round(getattr(t, "mEngineWaterTemp", 0), 1),
        "overheating": overheating(),
        "turboPressure": getattr(t, "mTurboBoostPresure", 0),
        "fuel": round(getattr(t, "mFuel", 0), 1),
        "capacityTank": getattr(t, "mFuelCapacity", 0),
        "averageFuelLap": fuel_per_lap()[1],
        "currentFuelLap": fuel_per_lap()[0],
        "estimatedLapFuel": fuel_per_lap()[2]
    })


################################# Driver Data #################################

def telemetry():
    global current_throttle, current_brake, current_direc, best_lap_telemetry_throttle, best_lap_telemetry_brake, best_lap_telemetry_direc, t

    throttle_live = getattr(t, "mUnfilteredThrottle", 0.0)
    brake_live = getattr(t, "mUnfilteredBrake", 0.0)
    direc_live = getattr(t, "mUnfilteredSteering", 0.0)
    throttle_live_smooth = getattr(t, "mFilteredThrottle", 0.0)
    brake_live_smooth = getattr(t, "mFilteredBrake", 0.0)
    direc_live_smooth = getattr(t, "mFilteredSteering", 0.0)

    return {
        "live_throttle": throttle_live,
        "live_brake": brake_live,
        "live_direc": direc_live,
        "live_throttle_smooth": throttle_live_smooth,
        "live_brake_smooth": brake_live_smooth,
        "live_direc_smooth": direc_live_smooth,
    }

@app.route("/driver_infos")
def driver_infos():
    if not info.isRF2running() or not info.isSharedMemoryAvailable():
        return jsonify({"status": "not ready"})

    return jsonify({
        "telemetry" : telemetry(),
    })

################################# Tire Data #################################

@app.route("/tire_infos")

#def get_tire_estimation():
 #   ...
def tire_infos():
    if not info.isRF2running() or not info.isSharedMemoryAvailable():
        return jsonify({"status": "not ready"})
    return jsonify({
        "front_Left_Wear": t.mWheels[0].mWear,
        "front_Right_Wear": t.mWheels[1].mWear,
        "rear_Left_Wear": t.mWheels[2].mWear,
        "rear_Right_Wear": t.mWheels[3].mWear,
        "front_Left_Temp": fahrenheit_to_celsius((t.mWheels[0].mTemperature[0] + t.mWheels[0].mTemperature[1] + t.mWheels[0].mTemperature[2]) / 3),
        "front_Right_Temp": fahrenheit_to_celsius((t.mWheels[1].mTemperature[0] + t.mWheels[1].mTemperature[1] + t.mWheels[1].mTemperature[2]) / 3),
        "rear_Left_Temp": fahrenheit_to_celsius((t.mWheels[2].mTemperature[0] + t.mWheels[2].mTemperature[1] + t.mWheels[2].mTemperature[2]) / 3),
        "rear_Right_Temp": fahrenheit_to_celsius((t.mWheels[3].mTemperature[0] + t.mWheels[3].mTemperature[1] + t.mWheels[3].mTemperature[2]) / 3)
    })

###############################################################################

@app.route("/")
def serve_home():
    return send_from_directory("static", "index.html")

@app.route("/diagnostic")
def diagnostic():
    return jsonify({
        "RF2_running": info.isRF2running(),
        "SharedMemory available": info.isSharedMemoryAvailable(),
        "Lap": getattr(t, "mLapNumber", "N/A"),
        "Speed": getattr(t.mLocalVel, "x", "N/A"),
        "Fuel": getattr(t, "mFuel", "N/A"),
        "BestLapTime": getattr(s, "mBestLapTime", "N/A")
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50000, ssl_context=('static/https/cert.pem', 'static/https/key.pem'), debug=False)

#python -m http.server 8000 
#https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin/blob/master/Monitor/rF2SMMonitor/rF2SMMonitor/rF2Data.cs
#https://github.com/TonyWhitley/pyRfactor2SharedMemory