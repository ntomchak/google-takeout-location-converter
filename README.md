Converts Google Takeout location data to GeoJSON format. Generates a file with place visit points and another with trip routes.

# Installation
1. Clone the repository and place takeout data in the same directory as the scripts with the directory name 'Takeout'
2. Install the latest version of python https://www.python.org/downloads/
3. Install pip https://pip.pypa.io/en/stable/installation/
4. Install geojson with the command `pip install geojson`

# Usage
1. Navigate to the scripts in the console (`cd /path/to/scripts/directory`)
2. Use `python3 convert.py`, or `py convert.py` if using Windows
   - Use -s and -e options to specify a start date and end date to convert (`python3 convert.py -s 2023-01-01 -e 2023-11-15`)
