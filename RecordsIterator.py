import os, json, utilities
from datetime import datetime

class Record:
    def __init__(self, raw_obj):
        self.lat = raw_obj["latitudeE7"] / 10**7 if "latitudeE7" in raw_obj else None
        self.lon = raw_obj["longitudeE7"] / 10**7 if "longitudeE7" in raw_obj else None
        
        self.properties = {}
        self.properties["timestamp"] = utilities.timestamp_to_datetime(raw_obj["timestamp"])
        self.properties["accuracy"] = raw_obj["accuracy"] if "accuracy" in raw_obj else None
        self.properties["deviceTag"] = raw_obj["deviceTag"] if "deviceTag" in raw_obj else None
        self.properties["source"] = raw_obj["source"] if "source" in raw_obj else None
        
        self.properties["altitude"] = raw_obj["altitude"] if "altitude" in raw_obj else None
        self.properties["verticalAccuracy"] = raw_obj["verticalAccuracy"] if "verticalAccuracy" in raw_obj else None
        self.properties["batteryCharging"] = raw_obj["batteryCharging"] if "batteryCharging" in raw_obj else None
        self.properties["formFactor"] = raw_obj["formFactor"] if "formFactor" in raw_obj else None
        self.properties["osLevel"] = raw_obj["osLevel"] if "osLevel" in raw_obj else None
        self.properties["velocity"] = raw_obj["velocity"] if "velocity" in raw_obj else None
        self.properties["heading"] = raw_obj["heading"] if "heading" in raw_obj else None
        self.properties["deviceDesignation"] = raw_obj["deviceDesignation"] if "deviceDesignation" in raw_obj else None

class RecordsIterator:
    def __init__(self, path):
        json_obj = utilities.json_from_path(path)
        self.iterator = iter(json_obj["locations"])
        self.current = None
    
    def next(self):
        nextt = next(self.iterator, None)
        if nextt is None:
            return None
        self.current = Record(nextt)
        return self.current