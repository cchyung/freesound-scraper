# Freesounds.org Scraper
This is a tool to retrieve data and download sounds from `freesounds.org`.

This can be used to generate a dataset for audio classification experiments!

## Setup
To use this tool you need to sign up and get API credentials from [https://freesound.org/apiv2/apply/]

Then save your credentials in a file called `credentials.json`:
```
{
	"client_id": <your client id>,
	"client_secret": <your client secret>
}
```

## How to Run
### Install Dependencies
First make sure that you have the following dependencies installed:

```
requests
tqdm
matplotlib
pandas
requests_oauthlib
numpy
```

Alternatively, you can run 
```
$ pip install -r requirements.txt
```

### Running
To run the tool use
```
$ python freesounds_scraper.py
```

By default, it expects you to have a csv file named `query.csv` of the queries that you want to make in the following format:
```
<query>,<number of samples to retrieve>
```

### Downloading Samples
To download the samples that you retrieve use the `--download True`:
```
 $ python freesounds_scraper.py --download True
```

After it retrieves all the data and saves it to the `csv` file, the tool will ask you to authenticate (because the API requires OAuth2 permissions to download)

Visit the authorize link that is output to the terminal and paste back in the code you get to download the samples!


### Retrieve Pack Data
You can also provide a list of pack ids in a file if you want to download certain packs:
```
$ python freesounds_scraper.py --pack-query <file name>
```

### Other Arguments
More customization for output files, appending more smaples to existing data, etc. can be found using 
```
$ python freesounds_scraper.py -h
```