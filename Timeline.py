# arguments: time threshold for same activity, 10 min default; start date, end date, records.json location
import os, json, utilities
from datetime import datetime

class TimelineObject:
    def __init__(self, raw_obj):
        self.start_time = utilities.timestamp_to_datetime(raw_obj["duration"]["startTimestamp"])
        self.end_time = utilities.timestamp_to_datetime(raw_obj["duration"]["endTimestamp"])

class PlaceVisit(TimelineObject):
    def __init__(self, raw_obj):
        TimelineObject.__init__(self, raw_obj)
        self.lat = raw_obj["location"]["latitudeE7"] / 10**7
        self.lon = raw_obj["location"]["longitudeE7"] / 10**7
        self.place_id = raw_obj["location"]["placeId"]
        self.address = raw_obj["location"]["address"] if 'address' in raw_obj["location"] else ''
        self.name = raw_obj["location"]["name"] if "name" in raw_obj["location"] else ''
        self.segment_type = 'place'
            
class ActivitySegment(TimelineObject):
    def _activity(self, raw_obj):
        if "activityType" in raw_obj:
            return raw_obj["activityType"]
        else:
            return raw_obj["activities"][0]["activityType"]

    def __init__(self, raw_obj):
        TimelineObject.__init__(self, raw_obj)
        self.activity_type = self._activity(raw_obj)
        self.segment_type = 'activity'

class Timeline:
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
            self.current_obj = PlaceVisit(parent_obj['placeVisit'])
            return self.current_obj
        else:
            self.current_obj = ActivitySegment(parent_obj['activitySegment'])
            return self.current_obj