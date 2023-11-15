import os, argparse, time
import load_data, generate_tables, write_geojson
from TimelineIterator import TimelineIterator
from RecordsIterator import RecordsIterator

start_seconds = time.time()

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start-date", type=str, default="2005-01-01", help="YYYY-MM-DD, filter by this date range")
parser.add_argument("-e", "--end-date", type=str, default="2100-01-01", help="YYYY-MM-DD, filter by this date range")
args = parser.parse_args()


data = load_data.load_data(args.start_date, args.end_date)


places = generate_tables.places(data[0])
activities = generate_tables.activities(data[1])
        
write_geojson.write_geojson(places, activities)

seconds_diff = time.time() - start_seconds

print(f"Took {seconds_diff} seconds")