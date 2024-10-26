import streamlit as st
import requests
import pandas as pd
import json

# Mapbox API key
MAPBOX_API_KEY = "pk.eyJ1IjoiYmFyYWRwcmF2ZWVua3VtYXIyIiwiYSI6ImNtMnBxZWhyczB0OXIybG9raXRiYW5pczMifQ.BFrFUI8el0qxXIA1_cTCFw"  # Replace with your actual API key

st.title("Location-Based Directions")
st.subheader("Get directions from your current location or enter a location manually")

# JavaScript to fetch current location and store it in localStorage
location_js = """
<script>
navigator.geolocation.getCurrentPosition(
    (position) => {
        const coords = {
            lat: position.coords.latitude,
            lon: position.coords.longitude
        };
        // Save coordinates to localStorage
        localStorage.setItem("user_coords", JSON.stringify(coords));
        document.dispatchEvent(new Event("user-location-fetched"));
    },
    (error) => {
        console.error("Error fetching location:", error);
        alert("Error fetching location: " + error.message);
        // Optional: You can notify that the location fetch failed
        document.dispatchEvent(new Event("location-fetch-failed"));
    }
);
</script>
"""

st.components.v1.html(location_js, height=0, width=0)

# Function to retrieve stored coordinates
def get_current_location():
    coords_str = st.session_state.get("user_coords_str", None)
    if coords_str:
        coords = json.loads(coords_str)
        return coords["lat"], coords["lon"]
    return None

# Function to get coordinates using Mapbox
def get_location_coordinates(location):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json?access_token={MAPBOX_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            return data["features"][0]["geometry"]["coordinates"][::-1]  # Convert to (lat, lon)
        else:
            st.error(f"No results found for '{location}'. Please try a different input.")
    else:
        st.error("Error fetching location data. Please check your API key or try again later.")
    return None

# Destination input
destination = st.text_input("Enter your destination (e.g., 'Golden Gate Bridge'): ")

# Placeholder for current location
current_location = st.empty()

# Add a button to get directions
if st.button("Get Directions"):
    start_coords = get_current_location()
    
    if start_coords:
        # Fetch destination coordinates
        destination_coords = get_location_coordinates(destination)
        if destination_coords:
            # Get directions using Mapbox Directions API
            directions_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_coords[1]},{start_coords[0]};{destination_coords[1]},{destination_coords[0]}?geometries=geojson&access_token={MAPBOX_API_KEY}"
            directions_response = requests.get(directions_url)
            
            if directions_response.status_code == 200:
                directions_data = directions_response.json()
                if "routes" in directions_data and len(directions_data["routes"]) > 0:
                    route = directions_data["routes"][0]["geometry"]["coordinates"]
                    directions_df = pd.DataFrame(route, columns=["longitude", "latitude"])
                    st.map(directions_df)  # Display the route on the map
                else:
                    st.error("Could not fetch route. Please try again.")
            else:
                st.error("Error fetching directions. Please check your API key or try again later.")
    else:
        # If current location fetch fails, allow user to enter their current location manually
        manual_location = st.text_input("Current Location (if GPS access failed):")
        if manual_location:
            start_coords = get_location_coordinates(manual_location)
            if start_coords:
                destination_coords = get_location_coordinates(destination)
                if destination_coords:
                    # Get directions using Mapbox Directions API
                    directions_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_coords[1]},{start_coords[0]};{destination_coords[1]},{destination_coords[0]}?geometries=geojson&access_token={MAPBOX_API_KEY}"
                    directions_response = requests.get(directions_url)
                    
                    if directions_response.status_code == 200:
                        directions_data = directions_response.json()
                        if "routes" in directions_data and len(directions_data["routes"]) > 0:
                            route = directions_data["routes"][0]["geometry"]["coordinates"]
                            directions_df = pd.DataFrame(route, columns=["longitude", "latitude"])
                            st.map(directions_df)  # Display the route on the map
                        else:
                            st.error("Could not fetch route. Please try again.")
                    else:
                        st.error("Error fetching directions. Please check your API key or try again later.")
        else:
            st.error("Could not fetch current location. Please ensure GPS access is allowed or enter your location manually.")
