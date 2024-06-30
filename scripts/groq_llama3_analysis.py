import os
from groq import Groq, RateLimitError
import pandas as pd
import json
import time
from dotenv import load_dotenv

load_dotenv()

# Load the dataset
data_file = '/Users/vihaanmotwani/Documents/OBD AI v2/data/sequential_obd_data.csv'
df = pd.read_csv(data_file)

# Assume a fuel tank capacity of 25 liters
FUEL_TANK_CAPACITY = 25

# Function to add calculated values to the dataset
def add_calculated_values(df):
    df['FUEL_CONSUMED'] = 0
    df['CO2_EMISSIONS'] = 0
    df['DISTANCE_TRAVELLED'] = 0
    
    for i in range(1, len(df)):
        initial_fuel_level = df.at[i-1, 'FUEL_LEVEL']
        final_fuel_level = df.at[i, 'FUEL_LEVEL']
        fuel_consumed = (initial_fuel_level - final_fuel_level) * FUEL_TANK_CAPACITY / 100
        df.at[i, 'FUEL_CONSUMED'] = fuel_consumed
        df.at[i, 'CO2_EMISSIONS'] = fuel_consumed * 1.61

        # Calculate distance travelled in the 10 second interval
        speed = df.at[i, 'SPEED']  # in km/h
        distance_travelled = speed * (10 / 3600)  # converting speed to km per 10 seconds
        df.at[i, 'DISTANCE_TRAVELLED'] = distance_travelled

    return df

# Update the dataset with calculated values
df = add_calculated_values(df)

# Function to calculate aggregated metrics for a batch
def calculate_metrics(batch_data):
    total_distance = sum(row['DISTANCE_TRAVELLED'] for row in batch_data)
    total_fuel_consumed = sum(row['FUEL_CONSUMED'] for row in batch_data)
    total_co2_emissions = sum(row['CO2_EMISSIONS'] for row in batch_data)
    
    if total_distance > 0:
        fuel_efficiency_l_100km = (total_fuel_consumed / total_distance) * 100
    else:
        fuel_efficiency_l_100km = 0
    
    co2_deviation = total_distance * 120 - total_co2_emissions * 1000  # Assuming average car emits 100g CO2/km

    return {
        "total_fuel_consumed": total_fuel_consumed,
        "fuel_efficiency_l_100km": fuel_efficiency_l_100km,
        "total_co2_emissions": total_co2_emissions,
        "co2_deviation": co2_deviation
    }

def prompt_edit(metrics, data):
    context = f"""
    You are an automotive expert and data analyst. Based on the following metrics, perform the following tasks:

    1. Analyze the fuel efficiency in liters per 100 kilometers (L/100km).

    2. Analyze the CO2 emissions based on the fuel consumption data.

    3. Provide actionable suggestions for improving fuel efficiency and reducing emissions. Include tips such as maintaining a steady speed, reducing idling time, and ensuring proper tire pressure.

    4. Mention the user's progress in a fun and engaging way. For example, if the CO2 deviation is positive, say, "You've saved approximately this many kgs of CO2 emissions, equivalent to planting this many trees!". If CO2 deviation is negative, say something alarming.

    Please ensure that your analysis and suggestions are detailed, clear, and easy to understand.

    Metrics:
    - Fuel Consumed (liters): {metrics['total_fuel_consumed']}
    - Fuel Efficiency (L/100km): {metrics['fuel_efficiency_l_100km']}
    - CO2 Emissions (kg): {metrics['total_co2_emissions']}
    - CO2 Deviation (grams): {metrics['co2_deviation']}

    OBD Data: {json.dumps(data)}

    Explanation of Variables:
    - ENGINE_LOAD (PID 04): Calculated Engine Load (Unit: percent)
    - COOLANT_TEMP (PID 05): Engine Coolant Temperature (Unit: Celsius)
    - SHORT_FUEL_TRIM_1 (PID 06): Short Term Fuel Trim - Bank 1 (Unit: percent)
    - LONG_FUEL_TRIM_1 (PID 07): Long Term Fuel Trim - Bank 1 (Unit: percent)
    - SHORT_FUEL_TRIM_2 (PID 08): Short Term Fuel Trim - Bank 2 (Unit: percent)
    - LONG_FUEL_TRIM_2 (PID 09): Long Term Fuel Trim - Bank 2 (Unit: percent)
    - FUEL_PRESSURE (PID 0A): Fuel Pressure (Unit: kilopascal)
    - RPM (PID 0C): Engine RPM (Unit: rpm)
    - MAF (PID 10): Air Flow Rate (MAF) (Unit: grams_per_second)
    - THROTTLE_POS (PID 11): Throttle Position (Unit: percent)
    - FUEL_LEVEL (PID 2F): Fuel Level Input (Unit: percent)
    - FUEL_RATE (PID 5E): Fuel rate
    - FUEL_STATUS (PID 03): Fuel System Status
    - DISTANCE_W_MIL (PID 21): Distance Traveled with MIL on (Unit: kilometer)
    - DISTANCE_SINCE_DTC_CLEAR (PID 31): Distance traveled since codes cleared (Unit: kilometer)
    """

    return context

def get_analysis(metrics, data, retry_attempts=3, retry_delay=10):

    # Initialize the Groq client
    client = Groq(
        api_key=os.environ.get("api_key"),
    )

    prompt = prompt_edit(metrics, data)
    
    for attempt in range(retry_attempts):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama3-70b-8192",
            )
            return chat_completion.choices[0].message.content
        except RateLimitError as e:
            print(f"Rate limit reached. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    return "Error: Unable to retrieve a valid response."

def parse_response(raw_response):
    return raw_response

if __name__ == "__main__":
    example_data = df.to_dict(orient='records')
    batch_size = 10
    output_file_path = '/Users/vihaanmotwani/Documents/OBD AI v2/output/analysis_output.txt'

    with open(output_file_path, 'w') as file:
        for i in range(0, len(example_data), batch_size):
            batch_data = example_data[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}")
            metrics = calculate_metrics(batch_data)
            raw_response = get_analysis(metrics, batch_data)
            response_message = parse_response(raw_response)
            file.write(f"Fuel Efficiency (L/100km): {metrics['fuel_efficiency_l_100km']}\n")
            file.write(f"CO2 Emissions (kg): {metrics['total_co2_emissions']}\n")
            file.write(f"CO2 deviation (g): {metrics['co2_deviation']}\n")
            file.write(f"Batch {i//batch_size + 1}:\n{response_message}\n\n")
            time.sleep(1)