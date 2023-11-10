import json
from geojson import Feature, FeatureCollection, LineString, Point

class Geojson:
    def __init__(self, data):
        with open('place_visits.json', 'w') as f:
            features = list(map(lambda place_data: self._point_to_feature(*place_data), data.place_visits))
            json.dump(FeatureCollection(features), f, indent=2)
        
        with open('place_visits_children.json', 'w') as f:
            features = list(map(lambda place_data: self._point_to_feature(*place_data), data.place_visits_children))
            json.dump(FeatureCollection(features), f, indent=2)
            
        with open('place_visits_other_candidate_locations.json', 'w') as f:
            features = list(map(lambda place_data: self._point_to_feature(*place_data), data.place_visits_other_candidate_locations))
            json.dump(FeatureCollection(features), f, indent=2)
            
        with open('place_visits_children_other_candidate_locations.json', 'w') as f:
            features = list(map(lambda place_data: self._point_to_feature(*place_data), data.place_visits_children_other_candidate_locations))
            json.dump(FeatureCollection(features), f, indent=2)
            
        with open('activity_segments.json', 'w') as f:
            activity_features = list(map(lambda activity_data: self._activity_to_feature(*activity_data), data.activities))
            json.dump(FeatureCollection(activity_features), f, indent=2)
        
    @staticmethod
    def _times_to_string(properties):
        if "duration_startTimestamp" and "duration_endTimestamp" in properties:
            properties["duration_endTimestamp"] = properties["duration_endTimestamp"].strftime('%Y-%m-%d %H:%M:%S')
            properties["duration_startTimestamp"] = properties["duration_startTimestamp"].strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def _point_to_feature(coords, properties):
        Geojson._times_to_string(properties)
        geojson_point = Point(coords)
        return Feature(geometry=geojson_point, properties=properties)
       
    @staticmethod
    def _activity_to_feature(coords, properties):
        Geojson._times_to_string(properties)
        line_string = LineString(coords)
        return Feature(geometry=line_string, properties=properties)