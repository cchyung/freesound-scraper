# deals with interacting with the freesounds.org API
from requests_oauthlib import OAuth2Session
import json
import os
import webbrowser
import requests

# define URL resources
BASE_URL = "https://freesound.org/apiv2"
SOUNDS = "/sounds"
SEARCH = "/search/text"
DOWNLOAD = "/download"
AUTHORIZE = "/oauth2/authorize"
ACCESS_TOKEN = "/oauth2/access_token"

# sample constants
# TODO: put constants in separate file
SAMPLES_PER_PAGE = 100
MAX_DURATION = 6 # in seconds

class ApiClient:
    def __init__(self, client_key, secret_key):
        self.client_key = client_key
        self.secret_key = secret_key
        self.oauth2_code = ''
    
    # returns True if authorization was successful, False otherwise
    def oauth2_authorize(self):
        oauth = OAuth2Session(
            self.client_key, redirect_uri='https://freesound.org/home/app_permissions/permission_granted/'
        )

        authorization_url, state = oauth.authorization_url(
            BASE_URL + AUTHORIZE
        )
        # open new browser
        webbrowser.open_new(authorization_url)

        # also print URL in case of remote session
        print('please visit the following URL to achieve authorization code %s' % (authorization_url, ))

        # request code from browser
        authorization_response=input("type in authorization code: ")
        r = requests.post(
            BASE_URL + ACCESS_TOKEN,
            params={
                'client_id': self.client_key,
                'client_secret': self.secret_key,
                'grant_type': 'authorization_code',
                'code': authorization_response
            }
        )

        if r.status_code != 200:
            print('error getting access token from the given authroization code')
            return False

        access_token = r.json()['access_token']
        self.oauth2_code = access_token
        return True
    
    def filter_string(self, file_type='wav', max_duration=MAX_DURATION, min_downloads=1000, min_avg_rating=4):
        return f'type:{file_type} duration:[* TO {max_duration}]num_downloads:[{min_downloads} TO *]avg_rating:[{min_avg_rating} TO *]is_remix:false'

    # returns json from API for processing
    def query(self, query='', page=1):
        params = {
            'token': self.secret_key,
            'query':query,
            'filter': self.filter_string('wav', MAX_DURATION, 1000, 4),
            'page': page,
            'page_size': SAMPLES_PER_PAGE
        }

        r = requests.get(BASE_URL + SEARCH, params=params)

        if r.status_code != 200:
            print("error getting samples for requested query...")
            return {}

        # parse response
        response = r.json()
        return response

    def download_sample(self, sample_id, file_name, target_directory):
        download_headers = {'Authorization': 'Bearer ' + self.oauth2_code}

        url = BASE_URL + SOUNDS + '/' + sample_id + DOWNLOAD
        response = requests.get(url, headers=download_headers)
        if response.status_code != 200:
            print('error downloading file with sample id %s' % (sample_id, ))
            return None
        
        with open(target_directory + '/' + file_name, 'wb') as f:
            f.write(response.content)
