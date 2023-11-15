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
        if "waypointPath" in raw_obj:
            self.properties["waypointPath_source"] = raw_obj["waypointPath"]["source"]
            self.properties["waypointPath_distanceMeters"] = raw_obj["waypointPath"]["distanceMeters"] if "distanceMeters" in raw_obj["waypointPath"] else None
            self.properties["waypointPath_travelMode"] = raw_obj["waypointPath"]["travelMode"] if "travelMode" in raw_obj["waypointPath"] else None
            self.properties["waypointPath_confidence"] = raw_obj["waypointPath"]["confidence"] if "confidence" in raw_obj["waypointPath"] else None
        
        self.transit_path = TransitPath(raw_obj["transitPath"]) if "transitPath" in raw_obj else None

class TransitStop:
    def __init__(self, transit_stop_obj, stop_time_obj):
        self.properties = {}
        self.lat = transit_stop_obj["latitudeE7"] / 10**7
        self.lon = transit_stop_obj["longitudeE7"] / 10**7
        self.properties["transitStop_placeId"] = transit_stop_obj["placeId"]
        self.properties["transitStop_address"] = transit_stop_obj["address"] if 'address' in transit_stop_obj else None
        self.properties["transitStop_name"] = transit_stop_obj["name"] if "name" in transit_stop_obj else None
        
        if stop_time_obj is not None:
            self.properties["stopTime_scheduledDepartureTimestamp"] = utilities.timestamp_to_datetime(stop_time_obj["scheduledDepartureTimestamp"]) if "scheduledDepartureTimestamp" in stop_time_obj else None
            self.properties["stopTime_scheduleArrivalTimestamp"] = utilities.timestamp_to_datetime(stop_time_obj["scheduleArrivalTimestamp"]) if "scheduleArrivalTimestamp" in stop_time_obj else None
            self.properties["stopTime_realtimeArrivalTimestamp"] = utilities.timestamp_to_datetime(stop_time_obj["realtimeArrivalTimestamp"]) if "realtimeArrivalTimestamp" in stop_time_obj else None
            self.properties["stopTime_realtimeDepartureTimestamp"] = utilities.timestamp_to_datetime(stop_time_obj["realtimeDepartureTimestamp"]) if "realtimeDepartureTimestamp" in stop_time_obj else None
        else:
            self.properties["stopTime_scheduledDepartureTimestamp"] = None
            self.properties["stopTime_scheduleArrivalTimestamp"] = None
            self.properties["stopTime_realtimeArrivalTimestamp"] = None
            self.properties["stopTime_realtimeDepartureTimestamp"] = None

class TransitPath:
    def __init__(self, transit_path_obj):
        self.properties = {}
        self.properties["name"] = transit_path_obj["name"]
        self.properties["linePlaceId"] = transit_path_obj["linePlaceId"] if "linePlaceId" in transit_path_obj else None
        self.properties["source"] = transit_path_obj["source"]
        self.properties["confidence"] = transit_path_obj["confidence"] if "confidence" in transit_path_obj else None
        self.properties["distanceMeters"] = transit_path_obj["distanceMeters"] if "distanceMeters" in transit_path_obj else None
        
        if ("stopTimesInfo" in transit_path_obj) and (len(transit_path_obj["stopTimesInfo"]) == len(transit_path_obj["transitStops"])):
            zipped_stops_with_times = zip(transit_path_obj["transitStops"], transit_path_obj["stopTimesInfo"])
            self.stops = list(map(lambda tup: TransitStop(tup[0], tup[1]), zipped_stops_with_times))
            self.properties["has_stop_times"] = 1
        else:
            self.stops = list(map(lambda stop: TransitStop(stop, None), transit_path_obj["transitStops"]))
            self.properties["has_stop_times"] = 0

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