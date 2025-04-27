import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()
opencage_key = os.getenv("OPENCAGE_KEY")

st.title("Classroom AC Temperature Calculator")
st.write("Calculate the optimal air conditioning temperature based on classroom parameters and local weather")

with st.form("calculator_form"):
    pincode = st.text_input("Pincode (India)", placeholder="e.g., 110001")
    num_people = st.number_input("Number of Students", min_value=1, max_value=100, value=30)
    
    st.subheader("Room Dimensions")
    col1, col2, col3 = st.columns(3)
    with col1:
        length = st.number_input("Length (m)", min_value=1.0, max_value=30.0, value=10.0, step=0.1)
    with col2:
        width = st.number_input("Width (m)", min_value=1.0, max_value=30.0, value=8.0, step=0.1)
    with col3:
        height = st.number_input("Height (m)", min_value=1.0, max_value=10.0, value=2.5, step=0.1)
    
    submitted = st.form_submit_button("Calculate Optimal Temperature")
    
    if submitted:
        try:
            # Get coordinates from pincode
            geo_url = f"https://api.opencagedata.com/geocode/v1/json?q={pincode}+India&key={opencage_key}"
            geo_response = requests.get(geo_url)
            geo_data = geo_response.json()
            
            if not geo_data['results']:
                st.error("Invalid pincode")
            else:
                lat = geo_data['results'][0]['geometry']['lat']
                lng = geo_data['results'][0]['geometry']['lng']
                location = geo_data['results'][0]['formatted']
                
                # Get weather data
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,relative_humidity_2m"
                weather_response = requests.get(weather_url)
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
                
                # Display results
                st.success(f"Optimal AC Temperature: {optimal_temp:.1f}°C")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Location Information")
                    st.write(f"**Location:** {location}")
                    st.write(f"**Current Temperature:** {current_temp}°C")
                    st.write(f"**Current Humidity:** {current_humidity}%")
                
                with col2:
                    st.subheader("Classroom Parameters")
                    st.write(f"**Number of Students:** {num_people}")
                    st.write(f"**Room Dimensions:** {length}m × {width}m × {height}m")
                    st.write(f"**Room Volume:** {room_vol} m³")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("Formula: T_opt = 24 - 0.1·(T_out-35) - 0.05·((RH_out-50)/10) - 0.02·(N-20) + 0.001·(V_room-150)")