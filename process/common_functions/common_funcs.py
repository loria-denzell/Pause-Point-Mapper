import re
from datetime import datetime 
from ..constants import *

def get_activity_type(line):
    match_tcx = re.search(REGEX_ACTIVITY_TYPE_TCX, line)
    match_gpx = re.search(REGEX_ACTIVITY_TYPE_GPX, line)
    activity = match_tcx.group(1) if match_tcx else match_gpx.group(1) if match_gpx else line
    return f'{ERROR_FILE_ACTIVITY_NOT_VALID_RIDE} <strong>{activity}</strong>'

def get_coord(line):
    coord = re.search(REGEX_NUMERIC_WITH_DECIMALS, line)
    return round(float(coord.group()), 5) if coord else None

def get_elev(line):
    elev = re.search(REGEX_NUMERIC_WITH_DECIMALS, line)
    return float(elev.group()) if elev else 0.0

def get_time(line):
    time_match = re.search(REGEX_DATETIME_WITH_MS, line)
    return adjust_datetime(time_match.group(1).replace(SUBSTRING_TO_FIND_MILLISECONDS, '')) if time_match else None

def get_name(line):
    name_match = re.search(REGEX_ACTIVITY_NAME, line)
    name = name_match.group(1).strip() if name_match else None
    return name if name and not name.isspace() else None

def adjust_datetime(datetime_input):
    datetime_input = datetime.strptime(re.sub(REGEX_DATETIME_REMOVE_DECIMALS, '', datetime_input), FORMAT_DATETIME_CONVERSION)
    hour = datetime_input.strftime('%I')
    am_pm = datetime_input.strftime('%p')
    
    if am_pm == 'PM':
        hour = '12' if hour == '12' else str(int(hour) + 12)
    elif am_pm == 'AM' and hour == '12':
        hour = '00'
    formatted_datetime = datetime_input.strftime(FORMAT_YY_MM_DD) + ' ' + hour + datetime_input.strftime(FORMAT_MM_SS)
    return datetime.strptime(formatted_datetime, FORMAT_FINAL_DATETIME)

def add_commas(number):
    return "{:,}".format(number)