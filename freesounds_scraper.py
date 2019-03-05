# main driver for sounds scraper
from client import ApiClient
from data import SampleData
from tqdm import tqdm
import argparse
import csv
import os
import json

# used to split of CSV files to run separately and avoid rate limit issues when downloading
SPLIT_LENGTH = 1900

# attempts to retrieve a number of samples given a specific query and store them into data array
def retrieve_and_process(client, data, query, num_samples):
    print("running query '%s' for %i samples" % (query, num_samples))
    response = client.query(query)

    # can only retrieve at most number of samples available on website
    samples_to_retrieve = min(response['count'], num_samples)

    if samples_to_retrieve == 0:
            print("no samples found!")
            return

    samples_to_retrieve -= data.process_samples(response['results'], query, samples_to_retrieve)
    
    page = 2
    while samples_to_retrieve > 0:
        response = client.query(query, page)

        if response == {} or response['count'] == 0:
            print("no more samples found!")
            break
        samples_to_retrieve -= data.process_samples(response['results'], query, samples_to_retrieve)

def retrieve_packs(pack_query_file_name):
    if not os.path.isfile(pack_query_file_name):
        print("could not find file %s" % (pack_query_file_name, ))
        return

    # load credentials JSON file
    with open('credentials.json') as f:
        data = json.load(f)
        CLIENT_ID = data['client_id']
        SECRET_KEY = data['client_secret']

    # define classes for API for data management
    client = ApiClient(CLIENT_ID, SECRET_KEY)
    data = SampleData()
    
    pack_ids = []
    with open(pack_query_file_name) as f:
        for line in f:
            pack_ids.append(line)

    for pack_id in pack_ids:
        response = client.query_pack(pack_id)
        if response is not json({}):
            data.process_samples(response['results'], pack_id, response['count'])

    return data


def retrieve_samples(query):
    if not os.path.isfile(query):
        print("could not find file %s" % (query, ))
        return None

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

def download(data, download_location):
    # load credentials JSON file
    with open('credentials.json') as f:
        file_data = json.load(f)
        CLIENT_ID = file_data['client_id']
        SECRET_KEY = file_data['client_secret']

    # need oauth2 to download
    client = ApiClient(CLIENT_ID, SECRET_KEY)
    client.oauth2_authorize()
    data_to_download = data.data_array

    print("downloading %d samples to %s" % (data_to_download.shape[0], download_location))

    unsuccessful_downloads = []

    for row in tqdm(data_to_download):
        success = client.download_sample(row[0], row[1], download_location)
        if not success:
            unsuccessful_downloads.append(row)
    
    # delete unsuccessful downloads from data array
    data.remove_unsuccessful(unsuccessful_downloads)


def main(args):
    if(args.download_csv):
        download_location = args.target
        if not os.path.isdir(download_location):
            print("folder %s not found, creating" % (download_location, ))
            os.mkdir(download_location)
        download_csv(args.download_csv, download_location)
    else:
        data = SampleData()
        if(args.pack_query):
            data = retrieve_packs(args.pack_query)
        else:
            data = retrieve_samples(args.query)
        
        if data.data_array.shape[0] > 0:
            data.remove_duplicates()

        if(args.append_to_csv):
            if not os.path.isfile(args.append_to_csv):
                print("could not load file %s" % (args.append_to_csv, ))
            else:
                loaded_data = SampleData()
                loaded_data.load_from_csv(args.append_to_csv)
                data.combine(loaded_data)

        if(args.download):
            download_location = args.target
            if not os.path.isdir(download_location):
                print("folder %s not found, creating" % (download_location, ))
                os.mkdir(download_location)

            download(data, download_location)

        if(args.split):
            data.save_to_csv_split(args.data_file_name, SPLIT_LENGTH)
        else:
            data.save_to_csv(args.data_file_name)

def download_csv(csv_to_download, download_location):
    data = SampleData()
    data.load_from_csv(csv_to_download)
    if not os.path.isdir(download_location):
        print("folder %s not found, creating" % (download_location, ))
        os.mkdir(download_location)
    download(data, download_location)
    
if __name__== "__main__":
    # setup argument parser
    parser = argparse.ArgumentParser(description='Welcome to the freesounds.org parser!')
    parser.add_argument('--query', type=str, default='query.csv', help='location of csv containing queries')
    parser.add_argument('--download', type=bool, default=False, help='whether or not to download')
    parser.add_argument('--target', type=str, default='samples/', help='path to download samples to')
    parser.add_argument('--data-file-name', type=str, default='data', help='file name for CSV')
    parser.add_argument('--download-csv', type=str, help='download a pre-processed csv')
    parser.add_argument('--pack-query',  type=str, help='retrieve packs listed in input file')
    parser.add_argument('--append-to-csv', type=str, help='append to already existing csv')
    parser.add_argument('--split', type=bool, default=False, help='whether to split into multiple csv files for rate limit issues')
    args = parser.parse_args()

    # call main function
    main(args)