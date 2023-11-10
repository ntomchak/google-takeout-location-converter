from TimelineIterator import TimelineIterator
from RecordsIterator import RecordsIterator

class Data:
    def __init__(self, start_date, end_date):
        self._load_raw_from_file(start_date, end_date)

    def _load_raw_from_file(self, start_date, end_date):
        timeline = TimelineIterator(start_date, end_date, "Takeout/Location History/Semantic Location History")
        records = RecordsIterator("Takeout/Location History/Records.json")

        timeline_obj = timeline.next()
        record_obj = records.next()

        places = {}
        activities = {}
        
        segment_id = 1
        
        while timeline_obj is not None and record_obj is not None:
            if record_obj.time < timeline_obj.properties["duration_startTimestamp"]: # if current record is before timeline object
                record_obj = records.next()
            elif record_obj.time <= timeline_obj.properties["duration_endTimestamp"]: # if current record is before or at end of current timeline obj
                if timeline_obj.segment_type == 'place':
                    places[segment_id] = timeline_obj
                elif timeline_obj.segment_type == 'activity':
                    if segment_id in activities:
                        activities[segment_id][0].append((record_obj.lon, record_obj.lat))
                    else:
                        activities[segment_id] = ([(record_obj.lon, record_obj.lat)], timeline_obj.properties)
                    
                if record_obj.time == timeline_obj.properties["duration_endTimestamp"]:
                    timeline_obj = timeline.next()
                    segment_id += 1
                else:
                    record_obj = records.next()
            else: # if current record is after current timeline object
                timeline_obj = timeline.next()
                segment_id += 1
                
        self.activities = list(activities.values())
        self._places(places)

    def _places(self, places):
        self.place_visits = []
        self.place_visits_children = []
        self.place_visits_other_candidate_locations = []
        self.place_visits_children_other_candidate_locations = []
        place_visits_id = 0
        place_visits_children_id = 0
        place_visits_other_candidate_locations_id = 0
        place_visits_children_other_candidate_locations_id = 0
        for place in places.values():
            place.properties = {"id": place_visits_id} | place.properties
            place_coords = (place.lon, place.lat)
            self.place_visits.append((place_coords, place.properties))
            for candidate in place.otherCandidateLocations:
                candidate_coords = (candidate.properties.pop("location_lon"), candidate.properties.pop("location_lat"))
                candidate.properties = {"id": place_visits_other_candidate_locations_id, "fk_place_visit": place_visits_id} | candidate.properties
                self.place_visits_other_candidate_locations.append((candidate_coords, candidate.properties))
                place_visits_other_candidate_locations_id += 1
            for child in place.children:
                child.properties = {"id": place_visits_children_id, "fk_place_visit": place_visits_id} | child.properties
                child_coords = (child.lon, child.lat)
                self.place_visits_children.append((child_coords, child.properties))
                for child_candidate in child.otherCandidateLocations:
                    cc_coords = (child_candidate.properties.pop("location_lon"), child_candidate.properties.pop("location_lat"))
                    child_candidate.properties = {"id": place_visits_children_other_candidate_locations_id, "fk_place_child": place_visits_children_id} | child_candidate.properties
                    self.place_visits_children_other_candidate_locations.append((cc_coords, child_candidate.properties))
                    place_visits_children_other_candidate_locations_id += 1
                place_visits_children_id += 1
            place_visits_id += 1