
#GLOBAL CONSTANTS
#STRINGS
WEBSITE_NAME = 'PAUSE POINT MAPPER'
STRAVA_CLIENT_ID = '122410'
STRAVA_CLIENT_SECRET = '1997889b43194dbdcd1dc59701021cfd9d5737e3'
STR_START = 'START'
STR_FINISH = 'FINISH'
STR_STOP = 'STOP'
STR_HIGHEST = 'HIGHEST'
STR_LONGEST = 'LONGEST'
STR_RED = 'red'
STR_BLUE = 'blue'
STR_NA = 'N/A'
ACCEPTABLE_ACTIVITIES = ['cycling', 'road', 'biking', 'ride']
ACCEPTABLE_FILE_TYPES = ['tcx', 'gpx', 'fit']
#KEYS AND SUBKEYS
KEY_ACCESS_TOKEN = 'access_token'
KEY_CODE = 'code'
KEY_ENTRY = 'entry'
KEY_DICT_INFO = 'info'
KEY_FILE_INPUT = 'file_input'
KEY_START_DATE_LOCAL = 'start_date_local'
KEY_NAME = 'name'
KEY_ERROR_MSG = 'error_message'
KEY_DATA = 'data'
SUBKEY_DICT_VAL = 'val'
SUBKEY_DATETIME = 'datetime'
SUBKEY_LATITUDE = 'lat'
SUBKEY_LONGITUDE = 'lng'
SUBKEY_LON = 'lon'
SUBKEY_ELEVATION = 'elev'
SUBKEY_SKIP = 'skip'
SUBKEY_ADDRESS = 'address'
SUBKEY_STOP_COUNTER = 'stop_count'
SUBKEY_DISTANCE = 'distance'
SUBKEY_GAP_DURATION = 'gap_duration'
SUBKEY_ELEV_GAINED = 'elev_gained'
SUBKEY_GRADIENT = 'gradient'
SUBKEY_DATETIME_DEPARTED = 'datetime_left'
SUBKEY_CLUSTER_LABEL = 'cluster_label'
SUBKEY_IS_HIGHEST = 'is_highest'
SUBKEY_KM = 'km'
SUBKEY_ICON_PROPS = 'icon_props'
SUBKEY_COLOR = 'color'
SUBKEY_ICON = 'icon'
SUBKEY_PREFIX = 'prefix'
SUBKEY_MARKER_TYPE = KEY_TYPE = 'type'
SUBKEY_ICON_PREFIX = 'fa'
SUBKEY_AUTHORIZATION = 'Authorization'
SUBKEY_BG_COLOR = 'background-color'

#URLS/LINKS
DOMAIN = 'http://127.0.0.1:8000/'
REDIRECT_URI = f'{DOMAIN}exchange_token/' 
AUTH_URL = f"https://www.strava.com/oauth/authorize?client_id={STRAVA_CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&approval_prompt=force&scope=read,profile:read_all,activity:read,activity:read_all"
INDEX_PAGE = 'index.html'

#exchange_token function
ERROR_CODE_TOKEN = 'Error exchanging code for access token:'
SUCCESSFULL_TOKEN_EXCHANGE = 'Token exchange successful'
STRAVA_TOKEN_AUTH_URL = 'https://www.strava.com/oauth/token'
REDIRECT_SUCCESS_URL = 'http://127.0.0.1:8000/'

#strava_link_process function
ERROR_NO_ACTIVITY_ID = 'No Strava Activity or Invalid Input was found'
ERROR_NO_ACCESS_TOKEN = 'No Authorization token was found'

#get_response function
EXCEPTION_GET_RESPONSE_FUNC = 'Failed to fetch data - ' 
ERROR_API_RESPONSE_REASONS = f'<br><strong>Causes/Reason:<br></strong><ul><li>Unauthorized API for the activity of the user.</li><li>Your Access Token is expired (Re-Authorize the API Again by Visiting this link: <a href="{AUTH_URL}">Strava API Re-Authorization</a>)</li><li>The Activity Link you inputted might be a manual type activity (Check the Information by visiting the strava link)</ul>'

#fetch_strava_activity_info function
STRAVA_ACTIVITY_INFO_URL = 'https://www.strava.com/api/v3/activities/'
ERROR_STRAVA_ACTIVITY_NOT_VALID_RIDE = 'Strava Activity Link is not a Bicycle Ride.'

#file_validation function
ERROR_FILE_NOT_FOUND = 'File input is missing.'
ERROR_FILE_EMPTY = 'Uploaded file is empty.'
ERROR_FILE_TYPE_INVALID = 'Invalid file type. Only .gpx, .tcx and .fit file types are allowed.'

#parser function
ERROR_FILE_ACTIVITY_NOT_VALID_RIDE = 'Uploaded File Activity is not a type of <strong>Bicycle Ride</strong> instead it got a type of '
ERROR_MISSING_DATETIME = 'Missing Start Date & Time on line: '
ERROR_MISSING_ACTIVITY_NAME = 'Missing Activity Name on line: '
ERROR_MISSING_COORDINATES = 'Missing coordinates for trackpoint'
ERROR_MISSING_ELEVATION = 'Missing Elevation for trackpoint'
ERROR_MISSING_LATITUDE = f'{ERROR_MISSING_COORDINATES} (Latitude) on line: '
ERROR_MISSING_LONGITUDE = f'{ERROR_MISSING_COORDINATES} (Longitude) on line: '
EXCEPTION_PARSER_FUNC = 'Parsing Failed - '

#fit_parser function
EXCEPTION_FIT_PARSER_FUNC = f'FIT {EXCEPTION_PARSER_FUNC}'

FORMAT_TIME = '%A, %B %d, %Y %H:%M:%S'
REGEX_GPX_COORDS = 'lat="([^"]+)" lon="([^"]+)"'
TAGS_ACTIVITY = ['<Activity', '<type>']
TAGS_ELEVATION = ['<ele>', '<AltitudeMeters>']
TAGS_CLOSING_TRACKPOINT = ['</trkpt>', '</Trackpoint>']
TAG_TIME = '<time>'
TAGS_TIME = [TAG_TIME, '<Time>']

#data_analysis function
ERROR_CORRUPTED_DATETIME = 'The input file contains corrupted datetime data '
ERROR_NO_STOP = 'No Stops found along the route'
EXCEPTION_DATA_ANALYSIS_FUNC = 'Data Analysis Failed - '

#data_clustering function 
EXCEPTION_DATA_CLUSTERING_FUNC = 'Data Clustering Failed - '

#map_init function
EXCEPTION_MAP_INIT_FUNC = 'Map Initialization Failed - '

#setup_longest_stop_marker
EXCEPTION_SETUP_LONGEST_MARKER_FUNC = 'Setup Longest Marker Failed - '

#setup_popup_content function
FORMAT_DATETIME_DISPLAY = '%a %b. %d, %Y, %I:%M:%S %p'
RED_POPUP_COLOR = '#ff6666'
START_POPUP_COLOR = '#899090'
FINISH_POUP_COLOR = '#2eb82e'
STOP_POPUP_COLOR = '#54B4D3'
TAG_LEAFLET_POPUP_CLASS = '.leaflet-popup-content-wrapper, .leaflet-popup-tip'

#find_average_gap_duration function
EXCEPTION_FINDING_AVERAGE_GAP_FUNC = 'No valid entries found for calculating average gap duration.'

#get_tasks function
NOMINATIM_API_URL = 'https://nominatim.openstreetmap.org'

#reverse_geocode function
ERROR_REVERSE_GEOCODE_FAILED = 'Reverse Geocode Failed - '

#adjust_datetime function 
FORMAT_DATETIME_CONVERSION = '%Y-%m-%dT%H:%M:%SZ'
REGEX_DATETIME_REMOVE_DECIMALS = '\\.\\d+'
FORMAT_YY_MM_DD = '%Y-%m-%d'
FORMAT_MM_SS = ':%M:%S'
FORMAT_FINAL_DATETIME = '%Y-%m-%d %H:%M:%S'

#format_time function
STRING_TIME_FORMAT = '{:02}:{:02}:{:02}'

#get_coord function
REGEX_NUMERIC_WITH_DECIMALS = '(\\d+(\\.\\d+)?)'

#get_time function
REGEX_DATETIME_WITH_MS = '(\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{3})?Z)'
SUBSTRING_TO_FIND_MILLISECONDS = '.000'

#get_name function
REGEX_ACTIVITY_NAME = '<[^>]*>(.*?)<\\/[^>]*>'

#get_type function 
REGEX_ACTIVITY_TYPE_TCX = '<Activity\s+Sport="([^"]+)"'
REGEX_ACTIVITY_TYPE_GPX = '<type>(.*?)</type>'

#create_circle function
CIRCLE_RADIUS = 50

#dbscan_algo_configuration function
EARTH_RADIUS = 6371000
DEGREE_180 = 180
TARGET_RADIUS_DISTANCE = 50.0
MIN_NUM_OF_SAMPLES = 2

#reverse_geocode function
MAX_RETRIES = 3