import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_synthetic_data(rows=60):
    data = {
        "TIMESTAMP": [],
        "SPEED": [],
        "RPM": [],
        "THROTTLE_POS": [],
        "ENGINE_LOAD": [],
        "COOLANT_TEMP": [],
        "SHORT_FUEL_TRIM_1": [],
        "LONG_FUEL_TRIM_1": [],
        "SHORT_FUEL_TRIM_2": [],
        "LONG_FUEL_TRIM_2": [],
        "FUEL_PRESSURE": [],
        "MAF": [],
        "FUEL_LEVEL": [],
        "FUEL_RATE": [],
        "FUEL_STATUS": [],
        "DISTANCE_SINCE_DTC_CLEAR": [],
    }
    
    start_time = datetime.now()
    speed = 50  # starting speed in km/h
    rpm = 2000  # starting rpm
    throttle_pos = 20  # starting throttle position in percentage
    engine_load = 50  # starting engine load in percentage
    coolant_temp = 85  # starting coolant temperature in Celsius
    short_fuel_trim_1 = 0  # starting short term fuel trim - bank 1
    long_fuel_trim_1 = 0  # starting long term fuel trim - bank 1
    short_fuel_trim_2 = 0  # starting short term fuel trim - bank 2
    long_fuel_trim_2 = 0  # starting long term fuel trim - bank 2
    fuel_pressure = 300  # starting fuel pressure in kPa
    maf = 2.0  # starting MAF in grams per second
    fuel_level = 50  # starting fuel level in percentage
    fuel_rate = 8  # starting fuel rate
    fuel_status = 1  # starting fuel system status
    distance_since_dtc_clear = 0  # starting distance traveled since codes cleared in km

    for i in range(rows):
        timestamp = start_time + timedelta(seconds=10*i)
        
        speed = max(0, speed + np.random.randint(-2, 3))  # speed fluctuates between -2 and 2 km/h per 10 seconds
        rpm = max(700, rpm + np.random.randint(-50, 51))  # rpm fluctuates between -50 and 50 per 10 seconds
        throttle_pos = min(100, max(0, throttle_pos + np.random.randint(-2, 3)))  # throttle position fluctuates between -2 and 2
        engine_load = min(100, max(0, engine_load + np.random.randint(-1, 2)))  # engine load fluctuates between -1 and 1
        coolant_temp = min(120, max(70, coolant_temp + np.random.randint(-1, 2)))  # coolant temperature fluctuates between -1 and 1
        short_fuel_trim_1 = min(100, max(-100, short_fuel_trim_1 + np.random.randint(-1, 2)))  # short term fuel trim - bank 1 fluctuates
        long_fuel_trim_1 = min(100, max(-100, long_fuel_trim_1 + np.random.randint(-1, 2)))  # long term fuel trim - bank 1 fluctuates
        short_fuel_trim_2 = min(100, max(-100, short_fuel_trim_2 + np.random.randint(-1, 2)))  # short term fuel trim - bank 2 fluctuates
        long_fuel_trim_2 = min(100, max(-100, long_fuel_trim_2 + np.random.randint(-1, 2)))  # long term fuel trim - bank 2 fluctuates
        fuel_pressure = max(0, fuel_pressure + np.random.randint(-2, 3))  # fuel pressure fluctuates
        maf = max(0, maf + np.random.uniform(-0.1, 0.1))  # MAF fluctuates
        fuel_level = max(0, fuel_level - np.random.uniform(0.02, 0.05))  # fuel level decreases over time
        fuel_rate = max(0, fuel_rate + np.random.uniform(-0.1, 0.1))  # fuel rate fluctuates
        fuel_status = fuel_status  # assuming fuel status remains constant for simplicity
        distance_since_dtc_clear += speed / 3600 * 10  # distance traveled since codes cleared

        data["TIMESTAMP"].append(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        data["SPEED"].append(speed)
        data["RPM"].append(rpm)
        data["THROTTLE_POS"].append(throttle_pos)
        data["ENGINE_LOAD"].append(engine_load)
        data["COOLANT_TEMP"].append(coolant_temp)
        data["SHORT_FUEL_TRIM_1"].append(short_fuel_trim_1)
        data["LONG_FUEL_TRIM_1"].append(long_fuel_trim_1)
        data["SHORT_FUEL_TRIM_2"].append(short_fuel_trim_2)
        data["LONG_FUEL_TRIM_2"].append(long_fuel_trim_2)
        data["FUEL_PRESSURE"].append(fuel_pressure)
        data["MAF"].append(maf)
        data["FUEL_LEVEL"].append(fuel_level)
        data["FUEL_RATE"].append(fuel_rate)
        data["FUEL_STATUS"].append(fuel_status)
        data["DISTANCE_SINCE_DTC_CLEAR"].append(distance_since_dtc_clear)
    
    return pd.DataFrame(data)

# Create dataset
df = create_synthetic_data()

# Save to CSV for model input
df.to_csv('/Users/vihaanmotwani/Documents/OBD AI v2/data/sequential_obd_data.csv', index=False)