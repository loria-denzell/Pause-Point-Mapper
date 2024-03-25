import math
import time
import asyncio
import aiohttp
from datetime import timedelta
from sklearn.cluster import DBSCAN
from statistics import mean
from django.shortcuts import render
from folium import Map, Circle, Marker, Icon, Popup
from folium.plugins import AntPath
from .common_functions.common_funcs import add_commas
from .constants import *
from .common_functions import *
from .activity_parsers.fit_parser import fit_parser
from .activity_parsers.gpx_and_tcx_parser import gpx_and_tcx_parser
from .activity_parsers.strava_parser import strava_link_process

async def index(request):
    if request.method == 'POST':
        start_time = time.time()
        try:
            data_dict = dict_storage_initialization()
            data_dict = file_validation(request, data_dict) if int(request.POST['data_src_type']) == 1 else strava_link_process(request, data_dict) 
            data_dict = data_analysis(request, data_dict) 
            stops_dict = await data_clustering(data_dict) 
            data_dict = await map_init(data_dict, stops_dict) 
            end_time = time.time()
            data_dict[KEY_DICT_INFO][3][SUBKEY_DICT_VAL] = format_time((end_time - start_time))
            return render(request, INDEX_PAGE, {KEY_DICT_INFO: data_dict[KEY_DICT_INFO]}) 
        except Exception as e:
            return render(request, INDEX_PAGE, {KEY_ERROR_MSG: str(e)})
    else: 
        return render(request, INDEX_PAGE, {'oauth': AUTH_URL})

def dict_storage_initialization():
    data_dict = {
        KEY_DICT_INFO: {
            i: {'description': desc, SUBKEY_DICT_VAL: ''} for i, (desc, default_val) in enumerate([
                ('DATA SOURCE / FILE TYPE', ''),
                ('ACTIVITY NAME', ''),
                ('THRESHOLD DURATION INPUT (SECONDS)', ''),
                ('PROCESS EXECUTION TIME (HH:MM:SS)', ''),
                ('AVERAGE STOP DURATION TIME (HH:MM:SS)', ''),
                ('NUMBER OF STOPS', ''),
                ('TOTAL STOP DURATION TIME (HH:MM:SS)', ''),
                ('LONGEST STOP DURATION (HH:MM:SS)', ''),
                ('DATE TIME STARTED', ''),
                ('DATE TIME ENDED', ''),
                ('TOTAL DISTANCE TRAVELLED (KM)', 0),
                ('SAMPLING RATE INTERVAL MEAN (SECONDS)', ''),
            ])
        }
    }
    return data_dict

def file_validation(request, data_dict):
    try:
        if KEY_FILE_INPUT not in request.FILES:
            raise FileNotFoundError(ERROR_FILE_NOT_FOUND)
        
        if request.FILES[KEY_FILE_INPUT].size == 0:
            raise Exception(ERROR_FILE_EMPTY)
        
        uploaded_file = request.FILES[KEY_FILE_INPUT]
        file_type = uploaded_file.name.lower().split('.')[-1]
        data_dict[KEY_DICT_INFO][0][SUBKEY_DICT_VAL] = file_type.upper()

        if file_type not in ACCEPTABLE_FILE_TYPES:
            raise Exception(ERROR_FILE_TYPE_INVALID)
        
        return fit_parser(uploaded_file, data_dict) if file_type == ACCEPTABLE_FILE_TYPES[2] else gpx_and_tcx_parser(uploaded_file, data_dict)
    except Exception as e:
        raise Exception(e)

def data_analysis(request, data_dict):
    try:
        duration_range = float(request.POST.get('durationRange', 0))
        max_entry_key = None
        max_elev = float('-inf')
        total_stop_duration = total_distance = total_sampling_rate = sampling_rate_counter = 0
        coords_list = []
        last_key = len(data_dict) - 2

        for key in range(1, len(data_dict)-1):
            current_entry = data_dict[key]
            previous_entry = data_dict[key-1]
            
            current_datetime = current_entry.get(SUBKEY_DATETIME)
            previous_datetime = previous_entry.get(SUBKEY_DATETIME)
            gap = (current_datetime - previous_datetime).total_seconds()
      
            if gap < 0:
                raise Exception(f'{ERROR_CORRUPTED_DATETIME}(From `{current_datetime}` to `{previous_datetime}` the gap is `{gap}`)')
       
            if gap >= duration_range:
                data_dict[key][SUBKEY_SKIP] = key == last_key
                coords_list.append([current_entry.get(SUBKEY_LATITUDE), current_entry.get(SUBKEY_LONGITUDE)])
                total_stop_duration += gap
            else:
                total_sampling_rate += gap
                sampling_rate_counter += 1
            
            data_dict[key][SUBKEY_GAP_DURATION] = gap
            
            current_elev = current_entry.get(SUBKEY_ELEVATION, 0)
            previous_elev = previous_entry.get(SUBKEY_ELEVATION, 0)
            max_elev, max_entry_key = (current_elev, key) if current_elev > max_elev else (max_elev, max_entry_key)
            
            horizontal_distance = haversine(previous_entry.get(SUBKEY_LATITUDE, 0), previous_entry.get(SUBKEY_LONGITUDE, 0),
                                            current_entry.get(SUBKEY_LATITUDE, 0), current_entry.get(SUBKEY_LONGITUDE, 0))
            vertical_height = round((current_elev - previous_elev), 2)
            
            data_dict[key][SUBKEY_KM] = round((total_distance := total_distance + horizontal_distance), 2)
            data_dict[key][SUBKEY_DISTANCE] = horizontal_distance
            data_dict[key][SUBKEY_ELEV_GAINED] = vertical_height
        if not coords_list: 
            raise Exception(ERROR_NO_STOP)
        
        data_dict[KEY_DICT_INFO][6][SUBKEY_DICT_VAL] = format_time(total_stop_duration)
        data_dict[KEY_DICT_INFO][2][SUBKEY_DICT_VAL] = duration_range
        data_dict[KEY_DICT_INFO][10][SUBKEY_DICT_VAL] = round(total_distance, 2)
        data_dict[KEY_DICT_INFO][11][SUBKEY_DICT_VAL] = round(total_sampling_rate / sampling_rate_counter)
        data_dict[max_entry_key][SUBKEY_IS_HIGHEST] = True
        labels = dbscan_algo_configuration(coords_list)
        
        for coords, label in zip(coords_list, labels):
            for key, value in data_dict.items():
                if SUBKEY_LATITUDE in value and SUBKEY_LONGITUDE in value and value.get(SUBKEY_LATITUDE) == coords[0] and value.get(SUBKEY_LONGITUDE) == coords[1]:
                    value[SUBKEY_CLUSTER_LABEL] = label
        return data_dict
    except Exception as e:
        raise Exception(f'{EXCEPTION_DATA_ANALYSIS_FUNC}{e}')

async def data_clustering(data_dict):
    try:
        stops_dict = {}
        stop_counter = 1
        for key in range(1, len(data_dict)-1):
            current_entry = data_dict[key]
            if current_entry.get(SUBKEY_SKIP, True):
                continue
            
            current_cluster = current_entry.get(SUBKEY_CLUSTER_LABEL)
            if current_cluster == -1:
                stops_dict[key] = current_entry
                stops_dict[key][SUBKEY_ADDRESS] = await reverse_geocode(current_entry.get(SUBKEY_LATITUDE), current_entry.get(SUBKEY_LONGITUDE))
                stops_dict[key][SUBKEY_STOP_COUNTER] = stop_counter
                stops_dict[key][SUBKEY_DATETIME_DEPARTED] = calculate_time_departure(current_entry.get(SUBKEY_DATETIME), current_entry.get(SUBKEY_GAP_DURATION))
            elif current_cluster > -1:
                same_cluster = [v for v in data_dict.values() if v.get(SUBKEY_CLUSTER_LABEL) == current_cluster and not v.get(SUBKEY_SKIP, False)]
                highest_gap_entry = max(same_cluster, key=lambda x: x.get(SUBKEY_GAP_DURATION))
                highest_gap_entry[SUBKEY_GAP_DURATION] = sum(x.get(SUBKEY_GAP_DURATION) for x in same_cluster)
                highest_gap_entry[SUBKEY_DATETIME_DEPARTED] = calculate_time_departure(highest_gap_entry.get(SUBKEY_DATETIME), highest_gap_entry.get(SUBKEY_GAP_DURATION))
                highest_gap_entry[SUBKEY_STOP_COUNTER] = stop_counter
                highest_gap_entry[SUBKEY_ADDRESS] = await reverse_geocode(highest_gap_entry.get(SUBKEY_LATITUDE), highest_gap_entry.get(SUBKEY_LONGITUDE))
                stops_dict[key] = highest_gap_entry
                for entry_value in same_cluster:
                    entry_value[SUBKEY_SKIP] = True
            stop_counter += 1
        
        data_dict[KEY_DICT_INFO][5][SUBKEY_DICT_VAL] = add_commas(stop_counter-1) #STOP COUNTER STARTS WITH 1 FOR DISPLAY PURPOSE ONLY, MINUS ONE FOR ORIGINAL COUNT
        return dict(sorted(stops_dict.items(), key=lambda x: x[1][SUBKEY_DATETIME]))
    except Exception as e:
        raise Exception(f'{EXCEPTION_DATA_CLUSTERING_FUNC}{e}')

async def map_init(data_dict, stops_dict): 
    try:
        map_output = Map(location=[data_dict[0].get(SUBKEY_LATITUDE), data_dict[0].get(SUBKEY_LONGITUDE)], zoom_start=13)
        await setup_initial_markers(data_dict, map_output) 
        stops_dict = setup_longest_stop_marker(data_dict, stops_dict, map_output)
        setup_stop_markers(data_dict, stops_dict, map_output)

        route_coordinates_list = [
            (value.get(SUBKEY_LATITUDE), value.get(SUBKEY_LONGITUDE))
            for value in data_dict.values()
            if SUBKEY_LATITUDE in value
            and SUBKEY_LONGITUDE in value 
        ]
        
        AntPath(locations=route_coordinates_list, delay=2000, color=STR_RED).add_to(map_output)
        data_dict[KEY_DICT_INFO]['map_html'] = map_output._repr_html_()
        return data_dict
    except Exception as e:
        raise Exception(f'{EXCEPTION_MAP_INIT_FUNC}{e}')

async def setup_initial_markers(data_dict, map_output):
    markers_info = [
        {KEY_ENTRY: next((value for value in data_dict.values() if value.get(SUBKEY_IS_HIGHEST)), None), SUBKEY_ICON_PROPS: 
                    {SUBKEY_COLOR: 'darkred', SUBKEY_ICON: 'fa-mountain', SUBKEY_PREFIX: SUBKEY_ICON_PREFIX}, SUBKEY_MARKER_TYPE: STR_HIGHEST},
        {KEY_ENTRY: data_dict[0], SUBKEY_ICON_PROPS: 
                    {SUBKEY_COLOR: 'lightgray', SUBKEY_ICON: 'fa-bicycle', SUBKEY_PREFIX: SUBKEY_ICON_PREFIX}, SUBKEY_MARKER_TYPE: STR_START},
        {KEY_ENTRY: list(data_dict.values())[-1], SUBKEY_ICON_PROPS: 
                    {SUBKEY_COLOR: 'green', SUBKEY_ICON: 'fa-flag-checkered', SUBKEY_PREFIX: SUBKEY_ICON_PREFIX}, SUBKEY_MARKER_TYPE: STR_FINISH},
    ]
    for marker_info in markers_info:
        latitude, longitude = marker_info[KEY_ENTRY][SUBKEY_LATITUDE], marker_info[KEY_ENTRY][SUBKEY_LONGITUDE]
        marker_info[KEY_ENTRY][SUBKEY_ADDRESS] = await reverse_geocode(latitude, longitude)
        popup_message = set_popup_content(marker_info[SUBKEY_MARKER_TYPE], marker_info[KEY_ENTRY])
        create_marker([latitude, longitude], popup_message, marker_info[SUBKEY_ICON_PROPS], marker_info[SUBKEY_MARKER_TYPE]).add_to(map_output)

def setup_longest_stop_marker(data_dict, stops_dict, map_output):
    try:
        outlier_entries = [value for value in stops_dict.values() if value.get(SUBKEY_CLUSTER_LABEL) == -1]
        longest_outlier_stop = max(outlier_entries, key=lambda x: x.get(SUBKEY_GAP_DURATION)) if outlier_entries else {SUBKEY_GAP_DURATION : 0.0} 

        cluster_entries = [value for value in stops_dict.values() if value.get(SUBKEY_CLUSTER_LABEL) > -1]
        longest_cluster_stop = max(cluster_entries, key=lambda x: x.get(SUBKEY_GAP_DURATION)) if cluster_entries else longest_outlier_stop

        longest_stop = longest_cluster_stop if longest_cluster_stop.get(SUBKEY_GAP_DURATION) > longest_outlier_stop.get(SUBKEY_GAP_DURATION) else longest_outlier_stop
        data_dict[KEY_DICT_INFO][4][SUBKEY_DICT_VAL] = format_time(find_average_gap_duration(stops_dict)) if len(stops_dict) else 0
        stops_dict = {key: value for key, value in stops_dict.items() 
                    if value.get(SUBKEY_LATITUDE) != longest_stop.get(SUBKEY_LATITUDE) 
                    and value.get(SUBKEY_LONGITUDE) != longest_stop.get(SUBKEY_LONGITUDE) } if len(stops_dict) >= 1 else stops_dict
        data_dict[KEY_DICT_INFO][7][SUBKEY_DICT_VAL] = format_time(longest_stop.get(SUBKEY_GAP_DURATION))
        
        lat, lng = longest_stop.get(SUBKEY_LATITUDE), longest_stop.get(SUBKEY_LONGITUDE)
        popup_content = set_popup_content(STR_LONGEST, longest_stop)
        icon_props = {SUBKEY_COLOR: STR_RED, SUBKEY_ICON: 'fa-pause', SUBKEY_PREFIX:SUBKEY_ICON_PREFIX}
        create_marker([lat, lng], popup_content, icon_props, (f'{STR_LONGEST} {STR_STOP} # {longest_stop.get(SUBKEY_STOP_COUNTER)}')).add_to(map_output)
        create_circle([lat, lng], True).add_to(map_output)
        
        return stops_dict
    except Exception as e:
        raise Exception(f'{EXCEPTION_SETUP_LONGEST_MARKER_FUNC}{e}')

def setup_stop_markers(data_dict, stops_dict, map_output):
    icon_properties = { SUBKEY_COLOR : STR_BLUE }
    last_trackpoint = list(data_dict.values())[-1]
    data_dict[KEY_DICT_INFO][9][SUBKEY_DICT_VAL] = last_trackpoint.get(SUBKEY_DATETIME, STR_NA).strftime(FORMAT_TIME)
    for key, value in stops_dict.items():
        current_cluster = value.get(SUBKEY_CLUSTER_LABEL)
        tooltip_txt = f'{STR_STOP}#{value.get(SUBKEY_STOP_COUNTER)}'
        lat, lng = value.get(SUBKEY_LATITUDE), value.get(SUBKEY_LONGITUDE)
        popup = set_popup_content(STR_STOP, value)
        create_marker([lat, lng], popup, icon_properties, tooltip_txt).add_to(map_output)
        if current_cluster != -1:
            create_circle([lat, lng], False).add_to(map_output)

def set_popup_content(popup_type, entry):
    popup_title = f'<strong>{popup_type} (KM: {entry.get(SUBKEY_KM, 0)}):</strong>'
    popup_loc = f'<br>Location: {entry.get(SUBKEY_ADDRESS, STR_NA)}'
    counter = entry.get(SUBKEY_STOP_COUNTER, 0)
    popup_coords = f'<br>Coordinates: <a class="text-primary" href="https://www.google.com/maps?q={entry.get(SUBKEY_LATITUDE)},{entry.get(SUBKEY_LONGITUDE)}" target="_blank">{entry.get(SUBKEY_LATITUDE)}, {entry.get(SUBKEY_LONGITUDE)}</a>'
    popup_datetime_arrived = entry.get(SUBKEY_DATETIME, STR_NA).strftime(FORMAT_TIME)
    arrival_datetime_str = f'<br>Date & Time Arrived/Passed: {popup_datetime_arrived}'
    popup_elev = f'<br>Elevation/Altitude: {entry.get(SUBKEY_ELEVATION, 0)} MASL'
 
    if popup_type in {STR_START, STR_FINISH}:
        color = START_POPUP_COLOR if popup_type == STR_START else FINISH_POUP_COLOR
    elif popup_type == STR_HIGHEST:
        color = RED_POPUP_COLOR
    elif popup_type == STR_LONGEST:
        popup_title = f'<strong>{popup_type} {STR_STOP} #{counter} (KM: {entry.get(SUBKEY_KM, 0)}):</strong>'
        popup_stop_duration = f'<br>Stop Duration: {format_time(entry.get(SUBKEY_GAP_DURATION, 0))}'
        popup_datetime_departure = f'<br>Date & Time Departed: {entry.get(SUBKEY_DATETIME_DEPARTED).strftime(FORMAT_TIME)}'
        popup_str = f'{popup_title}{popup_loc}{popup_coords}{arrival_datetime_str}{popup_datetime_departure}{popup_stop_duration}{popup_elev}'
        return f'<style>{TAG_LEAFLET_POPUP_CLASS} {{ {SUBKEY_BG_COLOR} : {RED_POPUP_COLOR}; }}</style> {popup_str}'
    elif popup_type == STR_STOP:
        popup_title = f'<strong>{popup_type}#{counter} (KM: {entry.get(SUBKEY_KM, 0)}):</strong>'
        popup_stop_duration = f'<br>Stop Duration: {format_time(entry.get(SUBKEY_GAP_DURATION, 0))}'
        popup_datetime_departure = f'<br>Date & Time Departed: {entry.get(SUBKEY_DATETIME_DEPARTED).strftime(FORMAT_TIME)}'
        popup_str = f'{popup_title}{popup_loc}{popup_coords}{arrival_datetime_str}{popup_datetime_departure}{popup_stop_duration}{popup_elev}'
        return f'<style>{TAG_LEAFLET_POPUP_CLASS} {{ {SUBKEY_BG_COLOR}: {STOP_POPUP_COLOR}; }}</style> {popup_str}'
    popup_str = f'{popup_title}{popup_loc}{popup_coords}{arrival_datetime_str}{popup_elev}'
    return f'<style>{TAG_LEAFLET_POPUP_CLASS} {{ {SUBKEY_BG_COLOR} : {color}; }}</style> {popup_str}'

def create_marker(location, popup_message, icon_properties, tooltip_txt):
    marker = Marker(location=location, tooltip=tooltip_txt,popup=Popup(popup_message, max_width=600))
    marker.add_child(Icon(**icon_properties))
    return marker
    
def create_circle(location, isLongest):
    color = STR_RED if isLongest else STR_BLUE
    return Circle(location=location, radius=CIRCLE_RADIUS, color=color, fill=True, fill_color=color)

def dbscan_algo_configuration(coordinates):
    one_degree_latitude_length = (math.pi * EARTH_RADIUS) / DEGREE_180
    eps_in_degrees = TARGET_RADIUS_DISTANCE / one_degree_latitude_length
    dbscan = DBSCAN(eps=eps_in_degrees, min_samples=MIN_NUM_OF_SAMPLES)
    return dbscan.fit_predict(coordinates)

def calculate_time_departure(start, stop_duration):
    return start + timedelta(seconds=stop_duration)

def find_average_gap_duration(stops_dict):
    valid_gap_durations = [value[SUBKEY_GAP_DURATION] for value in stops_dict.values()]
    if valid_gap_durations:
        return round(mean(valid_gap_durations), 2)
    else:
        raise ValueError(EXCEPTION_FINDING_AVERAGE_GAP_FUNC)

def get_tasks(session, params, headers):
    tasks = []
    for param in params:
        url = f'{NOMINATIM_API_URL}/reverse?lat={param[SUBKEY_LATITUDE]}&lon={param[SUBKEY_LON]}&format=json'
        tasks.append(session.get(url, headers=headers, ssl=False))
    return tasks

async def reverse_geocode(latitude, longitude): 
    retry_count = 0
    error = None
    while retry_count < MAX_RETRIES:
        try:
            async with aiohttp.ClientSession() as session:
                params = {'format': 'json', SUBKEY_LATITUDE: latitude, SUBKEY_LON: longitude}
                headers = {
                    'User-Agent': 'PausePointMapper/1.0 Python-requests',
                    'Referer': DOMAIN  
                }
                tasks = get_tasks(session, [params], headers)
                responses = await asyncio.gather(*tasks)
                for response in responses:
                    data = await response.json()
                    address_parts = [data[SUBKEY_ADDRESS].get(key, '') for key in ['road', 'residential', 'town', 'state', 'region']]
                    formatted_address = ', '.join(filter(None, address_parts))
                    return formatted_address.strip()
        except aiohttp.ClientError:
            retry_count += 1
            await asyncio.sleep(1)
        except Exception as e:
            error = str(e)
    raise Exception(f'{ERROR_REVERSE_GEOCODE_FAILED} after {MAX_RETRIES} retries ({error})')

def format_time(time):
    return STRING_TIME_FORMAT.format(int(time // 3600), int((time // 60) % 60),int(time % 60))

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    r = 6371  
    return round(r * c, 4)

def print_dict(dict_input):
    for key, value in dict_input.items():
        print(f'{key}: {value}')