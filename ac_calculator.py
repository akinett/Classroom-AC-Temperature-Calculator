import requests

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")  
opencage_key = os.getenv("OPENCAGE_KEY")

def get_optimal_ac_temp(pincode, num_people, length, width, height, opencage_key):
    """Calculate optimal AC temperature based on weather and room conditions"""
    
    # Get coordinates from pincode
    geo_url = f"https://api.opencagedata.com/geocode/v1/json?q={pincode}+India&key={opencage_key}"
    geo_response = requests.get(geo_url)
    
    if geo_response.status_code != 200:
        return f"Error: Geocoding failed ({geo_response.status_code})"
    
    geo_data = geo_response.json()
    if not geo_data['results']:
        return "Error: Invalid pincode"
    
    lat = geo_data['results'][0]['geometry']['lat']
    lng = geo_data['results'][0]['geometry']['lng']
    location_name = geo_data['results'][0]['formatted']
    
    # Get weather data
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,relative_humidity_2m"
    weather_response = requests.get(weather_url)
    
    if weather_response.status_code != 200:
        return f"Error: Weather API failed ({weather_response.status_code})"
    
    weather_data = weather_response.json()
    current_temp = weather_data['current']['temperature_2m']
    current_humidity = weather_data['current']['relative_humidity_2m']
    
    # Calculate optimal temperature
    room_vol = length * width * height
    
    # Formula implementation
    base_temp = 24.0
    temp_adjustment = (
        -0.1 * (current_temp - 35)
        -0.05 * ((current_humidity - 50) / 10)
        -0.02 * (num_people - 20)
        +0.001 * (room_vol - 150)
    )
    
    optimal_temp = base_temp + temp_adjustment
    
    # Humidity adjustment
    if current_humidity > 80:
        optimal_temp -= 0.5 * ((current_humidity - 80) / 10)
    
    # Enforce boundaries
    optimal_temp = max(20.0, min(26.0, optimal_temp))
    
    # Return tuple with all relevant information
    return {
        "optimal_temp": optimal_temp,
        "current_temp": current_temp,
        "current_humidity": current_humidity,
        "location": location_name
    }

def validate_inputs(pincode, occupants, length, width, height):
    """Validate user inputs"""
    if not pincode.isdigit() or len(pincode) != 6:
        return "Invalid pincode format. Must be 6 digits."
    if occupants <= 0:
        return "Number of occupants must be positive."
    if any(dim <= 0 for dim in [length, width, height]):
        return "Room dimensions must be positive."
    return None

if __name__ == "__main__":
    print("Classroom AC Temperature Calculator")
    print("----------------------------------")
    
    try:
        pincode = input("Enter pincode (e.g., 110001): ")
        
        # First check if we can get weather data for this pincode
        test_result = get_optimal_ac_temp(pincode, 1, 1, 1, 1, opencage_key)
        
        if isinstance(test_result, dict):
            # Show the location and weather information
            print(f"\nLocation: {test_result['location']}")
            print(f"Current Temperature: {test_result['current_temp']}°C")
            print(f"Current Humidity: {test_result['current_humidity']}%")
            print("----------------------------------")
            
            # Now continue with room details
            occupants = int(input("Enter number of students: "))
            length = float(input("Enter room length (meters): "))
            width = float(input("Enter room width (meters): "))
            height = float(input("Enter room height (meters): "))
            
            validation_error = validate_inputs(pincode, occupants, length, width, height)
            if validation_error:
                print(f"\nError: {validation_error}")
            else:
                result = get_optimal_ac_temp(pincode, occupants, length, width, height, opencage_key)
                print(f"\nOptimal AC Temperature: {result['optimal_temp']:.1f}°C")
        else:
            # If there was an error with the geocoding
            print(f"\nError: {test_result}")
    except ValueError:
        print("\nError: Please enter valid numeric values.")

