from TimelineIterator import TimelineIterator
from RecordsIterator import RecordsIterator

# ( list((place visit obj, records[])),  list(((timeline obj, records[])) )
def load_data(start_date, end_date):
    timeline = TimelineIterator(start_date, end_date, "Takeout/Location History/Semantic Location History")
    records = RecordsIterator("Takeout/Location History/Records.json")

    timeline_obj = timeline.next()
    record_obj = records.next()

    # segment_id: (place visit obj, records[])
    places = {}
    
    # segment_id: (timeline obj, records[])
    activities = {}
    
    segment_id = 1
    
    def add_point(seg_id, timeline_obj_dict, timeline_obj, record_obj):
        if seg_id in timeline_obj_dict:
            timeline_obj_dict[seg_id][1].append(record_obj)
        else:
            timeline_obj_dict[seg_id] = (timeline_obj, [record_obj])
            
    while timeline_obj is not None and record_obj is not None:
        if record_obj.properties["timestamp"] < timeline_obj.properties["duration_startTimestamp"]: # if current record is before timeline object
            record_obj = records.next()
        elif record_obj.properties["timestamp"] <= timeline_obj.properties["duration_endTimestamp"]: # if current record is before or at end of current timeline obj
            
            if timeline_obj.segment_type == 'place':
                add_point(segment_id, places, timeline_obj, record_obj)
            elif timeline_obj.segment_type == 'activity':
                add_point(segment_id, activities, timeline_obj, record_obj)
                
            if record_obj.properties["timestamp"] == timeline_obj.properties["duration_endTimestamp"]:
                timeline_obj = timeline.next()
                segment_id += 1
            else:
                record_obj = records.next()
        else: # if current record is after current timeline object
            timeline_obj = timeline.next()
            segment_id += 1
            
    return (list(places.values()), list(activities.values()))