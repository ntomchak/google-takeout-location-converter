import json, os, threading
from geojson import Feature, FeatureCollection, LineString, Point

def _times_to_string(properties, *args):
    for key in args:
        if key in properties and properties[key] is not None:
            properties[key] = properties[key].strftime('%Y-%m-%d %H:%M:%S')

def _record_to_feature(coords, properties):
    _times_to_string(properties, "timestamp")
    geojson_point = Point(coords)
    return Feature(geometry=geojson_point, properties=properties)
    
def _transit_stop_to_feature(coords, properties):
    _times_to_string(properties, "stopTime_scheduledDepartureTimestamp", "stopTime_scheduleArrivalTimestamp", "stopTime_realtimeArrivalTimestamp", "stopTime_realtimeDepartureTimestamp")
    geojson_point = Point(coords)
    return Feature(geometry=geojson_point, properties=properties)

def _point_to_feature(coords, properties):
    _times_to_string(properties, "duration_startTimestamp", "duration_endTimestamp")
    geojson_point = Point(coords)
    return Feature(geometry=geojson_point, properties=properties)
   
def _coords_list_to_line_feature(coords_list, properties):
    line_string = LineString(coords_list)
    return Feature(geometry=line_string, properties=properties)
    
def _activity_to_feature(coords_list, properties):
    _times_to_string(properties, "duration_startTimestamp", "duration_endTimestamp")
    return _coords_list_to_line_feature(coords_list, properties)
    
def write_geojson(places, activities):
    os.makedirs('output', exist_ok=True)

    def write(to_features_function, data_list, file_name):
        with open(f"output/{file_name}.json", 'w') as f:
            features = list(map(lambda data: to_features_function(*data), data_list))
            json.dump(FeatureCollection(features), f, indent=2)
        
    write(_point_to_feature, places[0], 'place_visits')
    write(_point_to_feature, places[1], 'place_visits_children')
    write(_point_to_feature, places[2], 'place_visits_other_candidate_locations')
    write(_point_to_feature, places[3], 'place_visits_children_other_candidate_locations')
    write(_record_to_feature, places[4], 'place_visits_raw_points')
    write(_activity_to_feature, activities[0], 'activity_segments')
    write(_record_to_feature, activities[1], 'activity_segments_raw_points')
    write(_coords_list_to_line_feature, activities[2], 'transit_paths')
    write(_transit_stop_to_feature, activities[3], 'transit_path_stops')