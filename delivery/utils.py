import requests
from django.conf import settings

def get_lat_lon(address):
    """
    Converts an address to latitude and longitude using the Google Geocoding API.
    """
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": settings.GOOGLE_MAPS_API_KEY}
    response = requests.get(base_url, params=params).json()
    if response.get("status") == "OK" and response.get("results"):
        location = response["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    return None, None

def get_optimized_route(office, drop_points):
    """
    Fetches an optimized route using Google Routes API.
    """
    base_url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline,routes.legs"
    }
    
    # Convert drop points to valid waypoints
    waypoints = [{"location": {"latLng": {"latitude": lat, "longitude": lng}}} for lat, lng in drop_points]

    # Find the farthest location to set as the final destination
    farthest_point = max(drop_points, key=lambda point: (point[0] - office[0])**2 + (point[1] - office[1])**2)

    request_data = {
        "origin": {"location": {"latLng": {"latitude": office[0], "longitude": office[1]}}},
        "destination": {"location": {"latLng": {"latitude": farthest_point[0], "longitude": farthest_point[1]}}},  # Final stop
        "intermediates": waypoints[:-1],  # Exclude last stop from intermediates
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE_OPTIMAL",
        "departureTime": "now",  # Uses real-time traffic data
        "computeAlternativeRoutes": False,
        "routeModifiers": {
            "avoidTolls": False,
            "avoidHighways": False,
            "avoidFerries": False,
            "avoidIndoor": False
        }
    }

    response = requests.post(base_url, json=request_data, headers=headers)
    response_data = response.json()

    if "routes" in response_data:
        return response_data
    return None  # Return None if no route is found