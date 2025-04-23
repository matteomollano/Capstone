import ipdata, os
from dotenv import load_dotenv

# load api key from environment variables
load_dotenv()

# set the api key
ipdata.api_key = os.getenv('API_KEY')

def filter_response(response):
    fields_to_keep = ['ip', 'city', 'region', 'country_name', 'continent_name', 'latitude', 'longitude', 'flag', 'asn']
    filtered_response = {}
    for key in fields_to_keep:
        if key in response:
            filtered_response[key] = response[key]   
    return filtered_response

def get_ip_data(public_ip):
    response = ipdata.lookup(public_ip)
    filtered_response = filter_response(response)
    return filtered_response