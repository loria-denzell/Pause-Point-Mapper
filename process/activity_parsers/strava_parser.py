from django.http import HttpResponse
from django.shortcuts import redirect, render
from datetime import datetime, timedelta
from ..constants import *
from ..common_functions.common_funcs import get_activity_type
import requests

def exchange_token(request):
    access_token = request.POST.get(KEY_ACCESS_TOKEN) 
    code = request.GET.get(KEY_CODE)
    if code and access_token is None:
        payload = {
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            KEY_CODE: code,
            'grant_type': 'authorization_code'
        }
        response = requests.post(STRAVA_TOKEN_AUTH_URL, data=payload)
        if response.status_code == 200:
            access_token = response.json()[KEY_ACCESS_TOKEN]
            response = redirect(DOMAIN)
            response.set_cookie(KEY_ACCESS_TOKEN, access_token, max_age=86400)
            response.set_cookie(KEY_CODE, code, max_age=86400)
            return response
        else:
            return render(request, INDEX_PAGE, {KEY_ERROR_MSG: f'{ERROR_CODE_TOKEN} {response.status_code}'})
    
    cookie_token = request.COOKIES.get(KEY_ACCESS_TOKEN)
    if cookie_token is not None:
        response = HttpResponse(render(request, INDEX_PAGE, {'message': SUCCESSFULL_TOKEN_EXCHANGE}))
        return response
    
def strava_link_process(request, data_dict):
    try:
        access_token = request.COOKIES.get(KEY_ACCESS_TOKEN)
        link_input = request.POST.get('link_input')
        activity_id = link_input.split('/')[-1]
        
        if not activity_id:
            raise Exception(ERROR_NO_ACTIVITY_ID)
        if not access_token:
            raise Exception(ERROR_NO_ACCESS_TOKEN)
 
        data_dict = fetch_strava_activity_info(access_token, activity_id, data_dict)
        data_dict = fetch_strava_activity_streams(access_token, activity_id, data_dict)
        return data_dict
    except Exception as e:
        raise Exception(e)

def get_response(url, headers, params, fields):
    try:
        response = requests.get(url, headers=headers, params=params)
        status_code = response.status_code 
        
        if status_code == 401:
            redirect(AUTH_URL)

        response.raise_for_status()  
        fetched_data = response.json()

        return {field: fetched_data.get(field) for field in fields} if fields else fetched_data
    except Exception as e:
        raise Exception(f'{EXCEPTION_GET_RESPONSE_FUNC}{str(e)}{ERROR_API_RESPONSE_REASONS}')

def fetch_strava_activity_info(access_token, activity_id, data_dict):
    try:
        activity_url = f'{STRAVA_ACTIVITY_INFO_URL}{activity_id}'
        headers = {SUBKEY_AUTHORIZATION: 'Bearer ' + access_token}
        activity_fields = [KEY_NAME, SUBKEY_DISTANCE, 'elapsed_time', KEY_START_DATE_LOCAL, KEY_TYPE]
        params = {'include_all_efforts': 'false'}
        result = get_response(activity_url, headers, params, activity_fields)
        
        if result[KEY_TYPE].lower() not in ACCEPTABLE_ACTIVITIES:
            raise Exception(get_activity_type(result[KEY_TYPE]))
        
        data_dict[KEY_DICT_INFO][0][SUBKEY_DICT_VAL] = 'Strava API'
        data_dict[KEY_DICT_INFO][1][SUBKEY_DICT_VAL] = result[KEY_NAME]  
        data_dict[KEY_DICT_INFO][8][SUBKEY_DICT_VAL] = datetime.strptime(result[KEY_START_DATE_LOCAL], FORMAT_DATETIME_CONVERSION)
        data_dict[KEY_DICT_INFO][10][SUBKEY_DICT_VAL] = float(result[SUBKEY_DISTANCE])
        return data_dict
    except Exception as e:
        raise Exception(e)

def fetch_strava_activity_streams(access_token, activity_id, data_dict):
    streams_url = f'{STRAVA_ACTIVITY_INFO_URL}{activity_id}/streams'
    stream_types = ['time', SUBKEY_DISTANCE, 'latlng', 'altitude']
    headers = {SUBKEY_AUTHORIZATION: 'Bearer ' + access_token}
    params = {'keys': ','.join(stream_types)}
    result = get_response(streams_url, headers, params, {})
    trackpoint_id = 0
    datetime_started = data_dict[KEY_DICT_INFO][8][SUBKEY_DICT_VAL]
    data_dict[KEY_DICT_INFO][8][SUBKEY_DICT_VAL] = data_dict[KEY_DICT_INFO][8][SUBKEY_DICT_VAL].strftime(FORMAT_TIME)
    
    for data in zip(result[0][KEY_DATA], result[1][KEY_DATA], result[2][KEY_DATA], result[3][KEY_DATA]):
        data_dict[trackpoint_id] = {
            SUBKEY_LATITUDE: data[0][0],
            SUBKEY_LONGITUDE: data[0][1],
            SUBKEY_DISTANCE: data[1],
            SUBKEY_ELEVATION: data[2],
            SUBKEY_DATETIME: datetime_started+timedelta(seconds=data[3]) 
        }
        trackpoint_id += 1
    return data_dict
