# Freesounds.org Scraper
This is a tool to retrieve data and download sounds from `freesounds.org`.

This can be used to generate a dataset for audio classification experiments!

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
python freesounds_scraper.py
```

By default, it expects you to have a csv file named `query.csv` of the queries that you want to make in the following format:
```
<query>,<number of samples to retrieve>
```

To download the samples that you retrieve use `--download True`:

### Retrieve Pack Data
You can also provide a list of pack ids in a file if you want to download certain packs:
```
$ python freesounds_scraper.py --pack-query <file name>
```

