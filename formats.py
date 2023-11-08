import json
from geojson import Feature, FeatureCollection, LineString, Point

class Geojson:
    def __init__(self):
        self.segment_id = 0
        self.points = []
        self.activities = []
        self.current_line_feature = None
    
    def place(self, segment_id, timeline_obj):
        if self.segment_id == segment_id:
            return None
        else:
            self.segment_id = segment_id
            coordinates = (timeline_obj.lon, timeline_obj.lat)
            point = Point(coordinates)
            properties = {
                "place_id": timeline_obj.place_id, 
                "address": timeline_obj.address, 
                "name": timeline_obj.name, 
                "start_time": timeline_obj.start_time.strftime('%Y-%m-%d %H:%M:%S'), 
                "end_time": timeline_obj.end_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            feature = Feature(geometry=point, properties=properties)
            self.points.append(feature)
            
    def activity(self, segment_id, timeline_obj, record_obj):
        if self.segment_id == segment_id:
            self.current_line_feature['geometry']['coordinates'].append((record_obj.lon, record_obj.lat))
        else:
            self.segment_id = segment_id
            coordinates = [(record_obj.lon, record_obj.lat)]
            line = LineString(coordinates)
            properties = {"start_time": timeline_obj.start_time.strftime('%Y-%m-%d %H:%M:%S'), 
                "end_time": timeline_obj.end_time.strftime('%Y-%m-%d %H:%M:%S'), 
                "activity_type": timeline_obj.activity_type}
            feature = Feature(geometry=line, properties=properties)
            self.current_line_feature = feature
            self.activities.append(feature)
    
    def write(self):
        with open('places.json', 'w') as f:
            json.dump(FeatureCollection(self.points), f, indent=2)
        with open('activities.json', 'w') as f:
            json.dump(FeatureCollection(self.activities), f, indent=2)