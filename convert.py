import os, argparse
from Timeline import Timeline
from Records import Records
from formats import Geojson

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start-date", type=str, default="2006-01-01", help="YYYY-MM-DD, filter by this date range")
parser.add_argument("-e", "--end-date", type=str, default="2050-01-01", help="YYYY-MM-DD, filter by this date range")
args = parser.parse_args()


timeline = Timeline(args.start_date, args.end_date, "Takeout/Location History/Semantic Location History")
records = Records("Takeout/Location History/Records.json")

timeline_obj = timeline.next()
record_obj = records.next()
new_format = Geojson()
segment_id = 1

while timeline_obj is not None and record_obj is not None:
    if record_obj.time < timeline_obj.start_time:
        record_obj = records.next()
    elif record_obj.time >= timeline_obj.end_time:
        timeline_obj = timeline.next()
        segment_id += 1
    else:
        if timeline_obj.segment_type == 'place':
            new_format.place(segment_id, timeline_obj)
        elif timeline_obj.segment_type == 'activity':
            new_format.activity(segment_id, timeline_obj, record_obj)
        record_obj = records.next()
        
new_format.write()