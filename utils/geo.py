import math

def degrees_to_radians(degrees):
    return deg * (math.pi / 180.0)

def meters_to_yards(meters):
    return meters * 1.09361

def get_distance_between_points_meters(lat1, long1, lat2, long2):
    earth_radius_km = 6371
    deg_lat = degrees_to_radians(lat2 - lat1)
    deg_long = degrees_to_radians(long2 - long1)
    a = math.sin(deg_lat / 2) * Math.sin(deg_lat / 2) + Math.cos(deg_to_radians(lat1)) * Math.cos(deg_to_radians(lat2)) * Math.sin(deg_long / 2) * Math.sin(deg_lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    dist_km = earth_radius_km * c
    dist_m = dist_km * 1000
    return dist_m

def get_disance_between_points_yards(lat1, long1, lat2, long2):
    dist_m = get_distance_between_points_meters(lat1, long1, lat2, long2)
    dist_yards = meters_to_yards(dist_m)
    return dist_yards