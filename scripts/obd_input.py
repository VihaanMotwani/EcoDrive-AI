import obd
import time
import pandas as pd
import csv

# Connect to the OBD-II adapter
connection = obd.OBD()

# Ensure the connection is successful
if not connection.is_connected():
    print("Failed to connect to OBD-II adapter")
    exit()

# Define the OBD commands to query
commands = {
    'RPM': obd.commands.RPM,
    'SPEED': obd.commands.SPEED,
    'THROTTLE_POS': obd.commands.THROTTLE_POS,
    'COOLANT_TEMP': obd.commands.COOLANT_TEMP
}

# Initialize the CSV file
csv_file = 'obd_data.csv'
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    header = ['Timestamp'] + list(commands.keys())
    writer.writerow(header)

# Sampling loop
try:
    while True:
        data_row = [time.strftime('%Y-%m-%d %H:%M:%S')]
        
        for cmd_name, cmd in commands.items():
            response = connection.query(cmd)
            if response.value is not None:
                data_row.append(response.value.magnitude)
            else:
                data_row.append(None)
        
        # Write the data to CSV
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data_row)
        
        print(f"Data sampled at {data_row[0]}: {data_row[1:]}")
        
        # Wait for 10 seconds before the next sample
        time.sleep(10)

except KeyboardInterrupt:
    print("Data sampling stopped.")

finally:
    connection.close()
