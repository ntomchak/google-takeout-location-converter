# arguments: time threshold for same activity, 10 min default; start date, end date, records.json location
import os, json, utilities
from datetime import datetime

class TimelineObject:
    def __init__(self, raw_obj):
        self.properties = {}
        if "duration" in raw_obj:
            self.properties["duration_startTimestamp"] = utilities.timestamp_to_datetime(raw_obj["duration"]["startTimestamp"])
            self.properties["duration_endTimestamp"] = utilities.timestamp_to_datetime(raw_obj["duration"]["endTimestamp"])
        self.properties["editConfirmationStatus"] = (1 if raw_obj["editConfirmationStatus"] == "CONFIRMED" else 0) if "editConfirmationStatus" in raw_obj else None

class Location:
    def __init__(self, location_obj):
        self.properties = {}
        self.properties["location_lon"] = location_obj["longitudeE7"] / 10**7
        self.properties["location_lat"] = location_obj["latitudeE7"] / 10**7
        self.properties["location_placeId"] = location_obj["placeId"]
        self.properties["location_address"] = location_obj["address"] if 'address' in location_obj else None
        self.properties["location_name"] = location_obj["name"] if "name" in location_obj else None
        self.properties["location_semanticType"] = location_obj["semanticType"] if "semanticType" in location_obj else None
        self.properties["location_locationConfidence"] = location_obj["locationConfidence"] if "locationConfidence" in location_obj else None
        self.properties["location_calibratedProbability"] = location_obj["calibratedProbability"] if "calibratedProbability" in location_obj else None

class PlaceVisit(TimelineObject):
    def __init__(self, raw_obj):
        TimelineObject.__init__(self, raw_obj)
        self.segment_type = 'place'
        location = Location(raw_obj["location"])
        if "centerLatE7" in raw_obj and "centerLngE7" in raw_obj:
            self.lat = raw_obj["centerLatE7"] / 10**7
            self.lon = raw_obj["centerLngE7"] / 10**7
            self.properties["centerLatLon"] = 1
        else:
            self.lat = location.properties["location_lat"]
            self.lon = location.properties["location_lon"]
            self.properties["centerLatLon"] = 0
        self.properties["placeConfidence"] = raw_obj["placeConfidence"] if "placeConfidence" in raw_obj else None
        self.properties["visitConfidence"] = raw_obj["visitConfidence"] if "visitConfidence" in raw_obj else None
        self.properties["locationConfidence"] = raw_obj["locationConfidence"] if "locationConfidence" in raw_obj else None
        self.properties["placeVisitType"] = raw_obj["placeVisitType"] if "placeVisitType" in raw_obj else None
        self.properties = self.properties | location.properties
        self.otherCandidateLocations = map(Location, raw_obj["otherCandidateLocations"]) if "otherCandidateLocations" in raw_obj else []
        
class ParentPlaceVisit(PlaceVisit):
    def __init__(self, raw_obj):
        PlaceVisit.__init__(self, raw_obj)
        self.properties["placeVisitImportance"] = raw_obj["placeVisitImportance"]
        self.children = map(ChildPlaceVisit, raw_obj["childVisits"]) if "childVisits" in raw_obj else []
        
class ChildPlaceVisit(PlaceVisit):
    def __init__(self, raw_obj):
        PlaceVisit.__init__(self, raw_obj)
        self.properties["placeVisitLevel"] = raw_obj["placeVisitLevel"] if "placeVisitLevel" in raw_obj else None
            
class ActivitySegment(TimelineObject):   
    def __init__(self, raw_obj):
        self.segment_type = 'activity'
        TimelineObject.__init__(self, raw_obj)
        self.properties["activityType"] = raw_obj["activityType"] if "activityType" in raw_obj else None
        self.properties["confidence"] = raw_obj["confidence"] if "confidence" in raw_obj else None
        self.properties["distance"] = raw_obj["distance"] if "distance" in raw_obj else None
        self.properties["most_probable_activity"] = raw_obj["activities"][0]["activityType"]
        self.properties["most_probable_activity_probability"] = raw_obj["activities"][0]["probability"]
        for activity in raw_obj["activities"]:
            self.properties["activities_" + activity["activityType"]] = activity["probability"]
        if "waypointPath" in raw_obj:
            self.properties["waypointPath_source"] = raw_obj["waypointPath"]["source"]
            self.properties["waypointPath_distanceMeters"] = raw_obj["waypointPath"]["distanceMeters"] if "distanceMeters" in raw_obj["waypointPath"] else None
            self.properties["waypointPath_travelMode"] = raw_obj["waypointPath"]["travelMode"] if "travelMode" in raw_obj["waypointPath"] else None
            self.properties["waypointPath_confidence"] = raw_obj["waypointPath"]["confidence"] if "confidence" in raw_obj["waypointPath"] else None

class TimelineIterator:
    def __init__(self, start_date, end_date, path):
        self._end_date = utilities.timestamp_to_datetime(end_date)
        self._path = path
        self._current_month_year = utilities.timestamp_to_datetime(start_date).replace(day=1)
        self._current_iter = self._next_month_iter()
        self.current_obj = None
    
    def _increment_month(self):
        next_month = self._current_month_year.month + 1
        next_year = self._current_month_year.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        self._current_month_year = self._current_month_year.replace(year=next_year, month=next_month, day=1)
    
    def _next_month_iter(self):
        while self._current_month_year <= self._end_date:
            file_name = f"{self._current_month_year.year}_{self._current_month_year.strftime('%B').upper()}.json"
            file_path = os.path.join(self._path, str(self._current_month_year.year), file_name)
            self._increment_month()
            json_obj = utilities.json_from_path(file_path)
            if json_obj is None:
                continue
            return iter(json_obj["timelineObjects"])
        return None
    
    def _next_timeline_obj(self):
        nextt = next(self._current_iter, None)
        if nextt is None:
            self._current_iter = self._next_month_iter()
            if self._current_iter is None:
                return None
            else:
                return next(self._current_iter)
        else:
            return nextt
            
    def next(self):
        parent_obj = self._next_timeline_obj()
        if parent_obj is None:
            return None
        elif 'placeVisit' in parent_obj:
            self.current_obj = ParentPlaceVisit(parent_obj['placeVisit'])
            return self.current_obj
        else:
            self.current_obj = ActivitySegment(parent_obj['activitySegment'])
            return self.current_obj