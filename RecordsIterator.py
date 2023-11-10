import os, json, utilities
from datetime import datetime

class Record:
    def __init__(self, raw_obj):
        self.lat = raw_obj["latitudeE7"] / 10**7 if "latitudeE7" in raw_obj else None
        self.lon = raw_obj["longitudeE7"] / 10**7 if "longitudeE7" in raw_obj else None
        self.time = utilities.timestamp_to_datetime(raw_obj["timestamp"])
        self.valid = False if self.lat is None or self.lon is None else True

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