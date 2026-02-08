"""Configuration constants for mytt_scraper"""

# URLs
BASE_URL = "https://www.mytischtennis.de"
LOGIN_URL = f"{BASE_URL}/login"
COMMUNITY_URL = f"{BASE_URL}/community"

# API Endpoints
OWN_PROFILE_ENDPOINT = f"{COMMUNITY_URL}?show=everything&_data=routes%2F%24"
EXTERNAL_PROFILE_ENDPOINT = f"{COMMUNITY_URL}/external-profile?user-id={{user_id}}&show=everything&_data=routes%2F%24"

# Headers for API requests
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'de,en-US;q=0.9,en;q=0.8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': BASE_URL + '/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

# Browser context settings
BROWSER_CONTEXT = {
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'viewport': {'width': 1920, 'height': 1080},
    'locale': 'de-DE',
    'timezone_id': 'Europe/Berlin',
}

# Browser launch arguments
BROWSER_ARGS = ['--no-sandbox', '--disable-setuid-sandbox']

# Default directories
TABLES_DIR_NAME = 'tables'

# Login selectors
LOGIN_SELECTORS = [
    'input[name="email"], input[type="email"]',
    'input[name="password"], input[type="password"]',
]

LOGIN_BUTTON_SELECTORS = [
    'button[type="submit"]',
    'button:has-text("Einloggen")',
    'button:has-text("Login")',
    'button:has-text("Anmelden")',
    'input[type="submit"]',
]

# Search input selectors
SEARCH_INPUT_SELECTORS = [
    'input[placeholder*="Suche"]',
    'input[type="search"]',
    'input[name*="search"]',
    '#search-input',
]

# Table field definitions
CLUB_INFO_FIELDS = [
    'clubNr', 'association', 'season', 'group_name',
    'group_name_short', 'group_id'
]

TTR_RANKING_FIELDS = [
    'position', 'firstname', 'lastname', 'rank', 'germanRank',
    'clubSexRank', 'germanSexRank', 'fedRank', 'clubName', 'clubNr',
    'personId', 'matchCount', 'fewGames', 'gender', 'country',
    'continent', 'fedNickname', 'external_id', 'lastYearNoGames'
]

LEAGUE_TABLE_FIELDS = [
    'season', 'league', 'group_id', 'table_rank', 'teamname',
    'club_nr', 'team_id', 'own_points', 'other_points', 'tendency'
]

TTR_HISTORY_EVENTS_FIELDS = [
    'event_date_time', 'formattedEventDate', 'formattedEventTime',
    'event_name', 'event_id', 'type',
    'ttr_before', 'ttr_after', 'ttr_delta',
    'match_count', 'matches_won', 'matches_lost',
    'expected_result', 'alteration_constant'
]

TTR_HISTORY_MATCHES_FIELDS = [
    'event_id', 'event_name', 'event_date_time', 'formattedEventDate',
    'formattedEventTime', 'event_type', 'match_number', 'type',
    'own_person_id', 'own_person_name', 'own_team_name', 'own_ttr',
    'other_person_id', 'other_person_name', 'other_team_name', 'other_ttr',
    'ttr_before', 'ttr_after', 'scheduled', 'expected_result',
    'own_set1', 'own_set2', 'own_set3', 'own_set4', 'own_set5',
    'own_set6', 'own_set7', 'other_set1', 'other_set2', 'other_set3',
    'other_set4', 'other_set5', 'other_set6', 'other_set7',
    'own_sets', 'other_sets', 'own_points', 'other_points', 'other_w_r_l'
]

# Search results CSV fields
SEARCH_RESULTS_FIELDS = [
    'user_id', 'name', 'firstname', 'lastname', 'club', 'clubNr',
    'ttr', 'external_id', 'personId'
]

# Search endpoints
SEARCH_ENDPOINTS = [
    {
        'url': f"{COMMUNITY_URL}?search={{query}}&show=everything&_data=routes%2F%24",
        'name': 'Community search'
    },
]
