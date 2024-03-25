import re
from ..constants import *
from ..common_functions.common_funcs import get_activity_type, get_time, get_name, get_elev, get_coord

def gpx_and_tcx_parser(uploaded_file, data_dict):
    try:
        inside_trackpoint = False
        trackpoint_id = 0

        with uploaded_file.open(mode='rb') as file_to_read:
            file_content = file_to_read.read().decode('utf-8')
        
        for line_num, line in enumerate(file_content.splitlines(), start=1):
            if any(tag in line for tag in TAGS_ACTIVITY) and not inside_trackpoint:
                if not any(tag in line.lower() for tag in ACCEPTABLE_ACTIVITIES): 
                    raise Exception(get_activity_type(line))
            if any(tag in line for tag in [TAG_TIME, '<Id>']) and not inside_trackpoint:
                start_time = get_time(line) 
                data_dict[KEY_DICT_INFO][8][SUBKEY_DICT_VAL] = start_time.strftime(FORMAT_TIME) if start_time is not None else STR_NA
            elif '<name>' in line.lower():
                if act_name := get_name(line):
                    data_dict[KEY_DICT_INFO][1][SUBKEY_DICT_VAL] = act_name
                else:
                    raise Exception(f'{ERROR_MISSING_ACTIVITY_NAME}{line_num}')
            elif '<trkpt' in line:
                data_dict[trackpoint_id] = {}
                inside_trackpoint = True
                coords = re.search(REGEX_GPX_COORDS, line)
                if coords:
                    data_dict[trackpoint_id][SUBKEY_LATITUDE] = round(float(coords.group(1)), 5)
                    data_dict[trackpoint_id][SUBKEY_LONGITUDE] = round(float(coords.group(2)), 5)
                else:
                    raise Exception(f'{ERROR_MISSING_COORDINATES}{line_num}')
            elif '<Trackpoint>' in line:
                data_dict[trackpoint_id] = {}
            elif any(tag in line for tag in TAGS_ELEVATION):
                if (elev := get_elev(line)) is not None:
                    data_dict[trackpoint_id][SUBKEY_ELEVATION] = elev
                else:
                    raise Exception(f'{ERROR_MISSING_ELEVATION}{line_num}')
            elif any(tag in line for tag in TAGS_TIME):
                if trackpoint_time := get_time(line):
                    data_dict[trackpoint_id][SUBKEY_DATETIME] = trackpoint_time
                else: 
                    raise Exception(f'{ERROR_MISSING_DATETIME}{line_num}')
            elif '<LatitudeDegrees>' in line:
                if coord := get_coord(line):
                    data_dict[trackpoint_id][SUBKEY_LATITUDE] = coord
                else:
                    raise Exception(f'{ERROR_MISSING_LATITUDE}{line_num}')
            elif '<LongitudeDegrees>' in line:
                if coord := get_coord(line):
                    data_dict[trackpoint_id][SUBKEY_LONGITUDE] = coord
                else:
                    raise Exception(f'{ERROR_MISSING_LONGITUDE}{line_num}')
            elif any(tag in line for tag in TAGS_CLOSING_TRACKPOINT):
                inside_trackpoint = False
                trackpoint_id += 1
        return data_dict
    except Exception as e:
        raise Exception(f'{EXCEPTION_PARSER_FUNC}{e}')