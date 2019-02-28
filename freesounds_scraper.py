# main driver for sounds scraper
from client import ApiClient
from data import SampleData
from tqdm import tqdm
import argparse
import csv
import os



import json

# attempts to retrieve a number of samples given a specific query and store them into data array
def retrieve_and_process(client, data, query, num_samples):
    print("running query '%s' for %i samples" % (query, num_samples))
    response = client.query(query)

    # can only retrieve at most number of samples available on website
    samples_to_retrieve = min(response['count'], num_samples)
    samples_to_retrieve -= data.process_samples(response['results'], query, samples_to_retrieve)
    
    page = 2
    while samples_to_retrieve > 0:
        response = client.query(query, page)

        if response == {}:
            print("no more samples found!")
            break
        samples_to_retrieve -= data.process_samples(response['results'], query, samples_to_retrieve)

def retrieve(query):
    # load credentials JSON file
    with open('credentials.json') as f:
        data = json.load(f)
        CLIENT_ID = data['client_id']
        SECRET_KEY = data['client_secret']

    # define classes for API for data management
    client = ApiClient(CLIENT_ID, SECRET_KEY)
    data = SampleData()


    with open(query, 'rt') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            retrieve_and_process(client, data, row[0], int(row[1]))

    return data

def download(data_to_download, download_location):
    # load credentials JSON file
    with open('credentials.json') as f:
        data = json.load(f)
        CLIENT_ID = data['client_id']
        SECRET_KEY = data['client_secret']

    # need oauth2 to download
    client = ApiClient(CLIENT_ID, SECRET_KEY)
    client.oauth2_authorize()

    print("downloading %d samples to %s" % (data_to_download.shape[0], download_location))

    for row in tqdm(data_to_download):
        client.download_sample(row[0], row[1], download_location)

def main(query_file, data_file_name, download_location):
    if not os.path.isfile(query_file):
        print("could not find file %s" % (query_file, ))
        return

    if not os.path.isdir(download_location):
        print("folder %s not found, creating" % (download_location, ))
        os.mkdir(download_location)
    
    data = retrieve(query_file)
    data.save_to_csv(data_file_name)
    print(data.data_array)

    download(data.data_array, download_location)


    

if __name__== "__main__":
    # TODO: Set up argument parsing 
    parser = argparse.ArgumentParser(description='Welcome to the freesounds.org parser!')
    parser.add_argument('--query', nargs=1, type=str, default='query.csv', help='location of csv containing queries')
    parser.add_argument('--target', nargs=1, type=str, default='samples/', help='path to download samples to')
    parser.add_argument('--data', nargs=1, type=str, default='data.csv', help='file name for CSV')
    args = parser.parse_args()

    main(args.query,  args.data, args.target)
    
    