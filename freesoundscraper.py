# temp one page implementation
import json
import requests
import csv
import numpy as np
import pandas as pd
import os
import datetime
import webbrowser
import matplotlib as plt
from requests_oauthlib import OAuth2Session

# sample constants
SAMPLES_PER_PAGE = 15
MAX_TAGS = 10
MAX_DURATION = 6 # in seconds

# define URL resources
BASE_URL = "https://freesound.org/apiv2"
SOUNDS = "/sounds"
SEARCH = "/search/text"
DOWNLOAD = "/download"
AUTHORIZE = "/oauth2/authorize"

# where to download samples too
TARGET_DIR = 'tmp/'

def download_url(sample_id):
    return BASE_URL + SOUNDS + '/' + sample_id + DOWNLOAD

# load credentials JSON file
with open('credentials.json') as f:
    data = json.load(f)
    CLIENT_ID = data['client_id']
    SECRET_KEY = data['client_secret']

# authorize applications for download
def oauth2_authorize():
    oauth = OAuth2Session(
        CLIENT_ID, redirect_uri='https://freesound.org/home/app_permissions/permission_granted/'
    )

    authorization_url, state = oauth.authorization_url(
        'https://freesound.org/apiv2/oauth2/authorize/'
    )
    # open new browser
    webbrowser.open_new(authorization_url)

    # request code from browser
    authorization_response=input("type in authorization code: ")
    r = requests.post(
        'https://freesound.org/apiv2/oauth2/access_token/',
        params={
            'client_id': CLIENT_ID,
            'client_secret': SECRET_KEY,
            'grant_type': 'authorization_code',
            'code': authorization_response
        }
    )
    access_token = r.json()['access_token']
    return access_token

oauth2_code = oauth2_authorize()

# store results in numpy array
# strips file name and adds extension if not present
def process_file_name(file_name, file_type):
    file_name_without_extension = os.path.splitext(file_name)[0]
    file_name_without_extension = file_name_without_extension.replace('/', ' ')

    # append file type at end of stripped file name
    return file_name_without_extension.strip() + file_type

# TODO: Add more of these as they pop up
TAGS_TO_IGNORE = {
    'a',
    'the',
    'best',
    'dumb',
    'needs',
    'work',
    'but',
    'made',
    'it',
    'its',
    'start',
    'good',
    'pprojects',
    'think'
}

# convert tags to lower case and removes dumb tags like "a"
# returns False if all tags were pruned
def process_tags(tags):
    processed_tags = []

    for tag in tags:
        tag = tag.lower()
        tag = tag.replace('-', ' ')   # replace dashes with spaces
        if not tag in TAGS_TO_IGNORE:
            if not tag.isdigit() and not (tag == '808' or tag == '909'):
                processed_tags.append(tag)

    return processed_tags

# convert results json into a 2D numpy array
def convert_to_numpy_array(results, query):
    # allocate an empty data array
    data_array = np.empty(([0, MAX_TAGS + 2]))

    for idx, sound_file in enumerate(results):
        file_name = query + str(idx).zfill(5)    # generate file name based off query
        file_info = np.array([sound_file['id'], file_name], dtype='S128')
        processed_tags = process_tags(sound_file['tags'])
        tags = np.array(processed_tags[:MAX_TAGS])

        # if there is at least one tag after processing, otherwise ignore
        if len(tags) > 0:

            # pad missing tags with empty strings up to MAX_TAGS
            for i in range(MAX_TAGS - tags.shape[0]):
                tags = np.append(tags, [''])

            features = np.concatenate((file_info, tags))
            data_array = np.append(data_array, [features], axis=0)

    return data_array

def filter_string(file_type='wav', max_duration=MAX_DURATION, min_downloads=1000, min_avg_rating=4):
    return f'type:{file_type} duration:[* TO {max_duration}]num_downloads:[{min_downloads} TO *]avg_rating:[{min_avg_rating} TO *]is_remix:false'

# returns a numpy array of sample data based on a query and num_samples
def query(query='', num_samples=1):
    # params for authentication
    token_params = {'token': SECRET_KEY}
    # filter by high number of downloads and good average rating to ensure quality
    # also want to avoid remixed sounds probably
    search_params = {
        'query':query,
        'filter': filter_string('wav', MAX_DURATION, 1000, 4)
    }

    def page_params(page_num):
        return{'page': page_num}

    params = {**token_params, **search_params}
    r = requests.get(BASE_URL + SEARCH, params=params)

    if r.status_code != 200:
        print("error getting samples for requested query...")
        return []

    # parse response
    response = r.json()
    total_samples_found = response['count']

    # if there aren't enough samples
    num_samples = min(num_samples, total_samples_found)

    results = response['results'][:num_samples]
    page_idx=2 # start at next page
    while(len(results) < num_samples):
        params = {**params, **page_params(page_idx)}
        r = requests.get(BASE_URL + SEARCH, params=params)
        if r.status_code == 200:
            response = r.json()
            results.extend(response['results'][:num_samples - len(results)]) # only grab samples needed
        else:
            print("error getting more samples for this query...")
            break;

    print("%i samples found for query: '%s'" % (len(results), query))

    numpy_results = convert_to_numpy_array(results, query)

    return numpy_results

# takes in a dictionary of queries and the number of samples for that query
def multi_query(query_dict):
    print('beginning queries...')

    data_array = np.empty(([0, MAX_TAGS + 2]))

    for query_string, num_samples in query_dict.items():
        query_data = query(query_string, num_samples)
        data_array = np.append(data_array, query_data, axis=0)

    print('%i samples found total' % (data_array.shape[0], ))
    return data_array

download_headers = {'Authorization': 'Bearer ' + oauth2_code}

def download_and_save_sample(sample_id, file_name):
    url = download_url(sample_id)
    response = requests.get(url, headers=download_headers)
    with open(TARGET_DIR + file_name, 'wb') as f:
        f.write(response.content)

# takes numpy array and downloads samples to TARGET_DIR
def download_samples(data_to_download):
    samples_downloaded = 0
    print("downloading %d samples to %s" % (data_to_download.shape[0], TARGET_DIR))
    for idx, sample in enumerate(data_to_download):
        sample_id, file_name = (sample[0], sample[1])
        try:
            download_and_save_sample(sample_id, file_name)
            samples_downloaded+=1
        except Exception as e:
            # TODO: remove entry from numpy array if could not download
            print("error downloading file %s: %s" % (file_name, e.__str__()))

    print("finished! downloaded %i samples" % (samples_downloaded, ))

# save csv file containing file name and descriptors
def save_to_csv(numpy_array):
    print("saving data to csv file")
    file_name = datetime.datetime.now().__str__()
    np.savetxt(file_name + ".csv", numpy_array, delimiter=",",fmt="%s")

# returns a pandas data frame based on the counts of each unique tag found
def tag_statistics(data):
    all_tags = np.empty([0])
    for sample in data:
        all_tags = np.append(all_tags, sample[2:])
    all_tags = all_tags[all_tags != '']
    unique, counts = np.unique(all_tags, return_counts=True)
    counts_array = np.swapaxes(np.concatenate(([unique], [counts])), 0, 1)
    return pd.DataFrame(data=counts_array[0:, 0:], columns=['tag name', 'instances'])


# testing out
num = 21
test_query = {
    'kick': num,
    'snare': num,
    'clap': num,
    'hat': num,
    'perc': num,
}

data = multi_query(test_query)

#save_to_csv(data)

# download_samples(numpy_results)
