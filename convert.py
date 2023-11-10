import os, argparse
from TimelineIterator import TimelineIterator
from RecordsIterator import RecordsIterator
from formats import Geojson
from load_data import Data
import load_data

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start-date", type=str, default="2005-01-01", help="YYYY-MM-DD, filter by this date range")
parser.add_argument("-e", "--end-date", type=str, default="2100-01-01", help="YYYY-MM-DD, filter by this date range")
args = parser.parse_args()


data = Data(args.start_date, args.end_date)
        
Geojson(data)