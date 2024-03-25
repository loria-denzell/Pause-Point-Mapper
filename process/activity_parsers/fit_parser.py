import fitparse
from ..common_functions.common_funcs import get_activity_type
from ..constants import *

def fit_parser(file, data_dict):
    try:
        data_dict[KEY_DICT_INFO][1][SUBKEY_DICT_VAL] = file.name.split('.')[0]
        fitfile = fitparse.FitFile(file)
        trackpoint_id = 0
        for record in fitfile.get_messages():
            if record.name == 'session':
                for data in record:
                    if 'sport' in data.name and data.value not in ACCEPTABLE_ACTIVITIES:
                        raise Exception(get_activity_type(data.name))
                    if 'start_time' in data.name:
                        data_dict[KEY_DICT_INFO][8][SUBKEY_DICT_VAL] = data.value.strftime(FORMAT_TIME)
            elif record.name == 'record':
                data_dict[trackpoint_id] = {}
                for data in record:
                    if data.value is not None:
                        if 'lat' in data.name:
                            data_dict[trackpoint_id][SUBKEY_LATITUDE] = fit_coords_to_decimal(data.value)
                        elif 'long' in data.name:
                            data_dict[trackpoint_id][SUBKEY_LONGITUDE] = fit_coords_to_decimal(data.value)
                        elif 'altitude' in data.name:
                            data_dict[trackpoint_id][SUBKEY_ELEVATION] = round(float(data.value), 2)
                        elif 'timestamp' in data.name:
                            data_dict[trackpoint_id][SUBKEY_DATETIME] = data.value
                trackpoint_id += 1
        return data_dict
    except Exception as e:
        raise Exception(f'{EXCEPTION_FIT_PARSER_FUNC}{e}')

def fit_coords_to_decimal(value_to_convert):
    degrees = value_to_convert * (180.0 / (2**31))
    return round(float(degrees), 5)
