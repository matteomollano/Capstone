import ipdata, os, json
from dotenv import load_dotenv

def filter_response(response):
    fields_to_keep = ['ip', 'city', 'region', 'country_name', 'continent_name', 'latitude', 'longitude', 'flag', 'asn']
    filtered_response = {}
    for key in fields_to_keep:
        if key in response:
            filtered_response[key] = response[key]   
    return filtered_response

def get_ip_data(public_ip):
    try:
        load_dotenv()
        ipdata.api_key = os.getenv('API_KEY')
        response = ipdata.lookup(public_ip)
        filtered_response = filter_response(response)
        return filtered_response
    except Exception as e:
        return public_ip
       
def OK_status(response_json):
    status = response_json['status']
    if status == 200:
        return True
    return False

def get_domain_name(response_json):
    if not OK_status(response_json):
        return
    asn = response_json['asn']
    domain_name = asn['domain']
    return domain_name

def get_coordinates(response_json):
    if not OK_status(response_json):
        return
    latitude, longitude = response_json['latitude'], response_json['longitude']
    return latitude, longitude

# testing
# response_json = json.loads('{"ip": "142.250.65.238", "is_eu": false, "city": null, "region": null, "region_code": null, "region_type": null, "country_name": "United States", "country_code": "US", "continent_name": "North America", "continent_code": "NA", "latitude": 37.750999450683594, "longitude": -97.8219985961914, "postal": null, "calling_code": "1", "flag": "https://ipdata.co/flags/us.png", "emoji_flag": "🇺🇸", "emoji_unicode": "U+1F1FA U+1F1F8", "asn": {"asn": "AS15169", "name": "Google LLC", "domain": "google.com", "route": "142.250.65.0/24", "type": "business"}, "languages": [{"name": "English", "native": "English", "code": "en"}], "currency": {"name": "US Dollar", "code": "USD", "symbol": "$", "native": "$", "plural": "US dollars"}, "time_zone": {"name": null, "abbr": null, "offset": null, "is_dst": null, "current_time": null}, "threat": {"is_tor": false, "is_icloud_relay": false, "is_proxy": false, "is_datacenter": false, "is_anonymous": false, "is_known_attacker": false, "is_known_abuser": false, "is_threat": false, "is_bogon": false, "blocklists": []}, "count": "0", "status": 200}')

# amazon_json = {'ip': '54.239.28.85', 'is_eu': False, 'city': 'Ashburn', 'region': 'Virginia', 'region_code': 'VA', 'region_type': 'state', 'country_name': 'United States', 'country_code': 'US', 'continent_name': 'North America', 'continent_code': 'NA', 'latitude': 39.04372024536133, 'longitude': -77.48748779296875, 'postal': None, 'calling_code': '1', 'flag': 'https://ipdata.co/flags/us.png', 'emoji_flag': '🇺🇸', 'emoji_unicode': 'U+1F1FA U+1F1F8', 'asn': {'asn': 'AS16509', 'name': 'Amazon Inc', 'domain': 'amazon.com', 'route': '54.239.16.0/20', 'type': 'business'}, 'languages': [{'name': 'English', 'native': 'English', 'code': 'en'}], 'currency': {'name': 'US Dollar', 'code': 'USD', 'symbol': '$', 'native': '$', 'plural': 'US dollars'}, 'time_zone': {'name': 'America/New_York', 'abbr': 'EDT', 'offset': '-0400', 'is_dst': True, 'current_time': '2025-04-04T18:24:31-04:00'}, 'threat': {'is_tor': False, 'is_icloud_relay': False, 'is_proxy': False, 'is_datacenter': False, 'is_anonymous': False, 'is_known_attacker': False, 'is_known_abuser': False, 'is_threat': False, 'is_bogon': False, 'blocklists': []}, 'count': '0', 'status': 200}

'''
Filtered:
{
    "ip": "54.239.28.85",
    "city": "Ashburn",
    "region": "Virginia",
    "country_name": "United States",
    "continent_name": "North America",
    "latitude": 39.04372024536133,
    "longitude": -77.48748779296875,
    "flag": "https://ipdata.co/flags/us.png",
    "asn": {
        "asn": "AS16509",
        "name": "Amazon Inc",
        "domain": "amazon.com",
        "route": "54.239.16.0/20",
        "type": "business"
    }
}

Non-filtered:
{
    "ip": "54.239.28.85",
    "is_eu": false,
    "city": "Ashburn",
    "region": "Virginia",
    "region_code": "VA",
    "region_type": "state",
    "country_name": "United States",
    "country_code": "US",
    "continent_name": "North America",
    "continent_code": "NA",
    "latitude": 39.04372024536133,
    "longitude": -77.48748779296875,
    "postal": null,
    "calling_code": "1",
    "flag": "https://ipdata.co/flags/us.png",
    "emoji_flag": "\ud83c\uddfa\ud83c\uddf8",
    "emoji_unicode": "U+1F1FA U+1F1F8",
    "asn": {
        "asn": "AS16509",
        "name": "Amazon Inc",
        "domain": "amazon.com",
        "route": "54.239.16.0/20",
        "type": "business"
    },
    "languages": [
        {
            "name": "English",
            "native": "English",
            "code": "en"
        }
    ],
    "currency": {
        "name": "US Dollar",
        "code": "USD",
        "symbol": "$",
        "native": "$",
        "plural": "US dollars"
    },
    "time_zone": {
        "name": "America/New_York",
        "abbr": "EDT",
        "offset": "-0400",
        "is_dst": true,
        "current_time": "2025-04-04T18:36:25-04:00"
    },
    "threat": {
        "is_tor": false,
        "is_icloud_relay": false,
        "is_proxy": false,
        "is_datacenter": false,
        "is_anonymous": false,
        "is_known_attacker": false,
        "is_known_abuser": false,
        "is_threat": false,
        "is_bogon": false,
        "blocklists": []
    },
    "count": "0",
    "status": 200
}
'''