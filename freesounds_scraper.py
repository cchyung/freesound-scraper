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
        if response is not {}:
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


def main(args):
    if(args.download_csv):
        download_csv(args.download_csv)
    else:
        if(args.pack_query):
            data = retrieve_packs(args.pack_query[0])
        else:
            data = retrieve_samples(args.query[0])
        
        if(args.append_to_csv):
            if not os.path.isfile(args.append_to_csv[0]):
                print("could not load file %s" % (args.append_to_csv[0], ))
            loaded_data = SampleData()
            loaded_data.load_from_csv(args.append_to_csv[0])
            data.combine(loaded_data)

        data.save_to_csv(args.data)

        if(args.download):
            download_location = args.target
            if not os.path.isdir(download_location):
                print("folder %s not found, creating" % (download_location, ))
                os.mkdir(download_location)

            download(data.data_array, download_location)

def download_csv(csv_to_download):
    print("download csv")
    
if __name__== "__main__":
    # setup argument parser
    parser = argparse.ArgumentParser(description='Welcome to the freesounds.org parser!')
    parser.add_argument('--query', nargs=1, type=str, default='query.csv', help='location of csv containing queries')
    parser.add_argument('--download', nargs=1, type=bool, default=False, help='whether or not to download')
    parser.add_argument('--target', nargs=1, type=str, default='samples/', help='path to download samples to')
    parser.add_argument('--data', nargs=1, type=str, default='data.csv', help='file name for CSV')
    parser.add_argument('--download-csv', nargs=1, help='download a pre-processed csv')
    parser.add_argument('--pack-query', nargs=1, type=str, default='pack_query', help='retrieve packs listed in input file')
    parser.add_argument('--append-to-csv', nargs=1, type=str, help='append to already existing csv')
    args = parser.parse_args()

    # call main function
    main(args)