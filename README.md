# Freesounds.org Scraper
This is a tool to retrieve data and download sounds from `freesounds.org`.

This can be used to generate a dataset for audio classification experiments!

## How to Run
First make sure that you have the following dependencies installed:

```
requests==2.21.0
tqdm==4.31.1
matplotlib==2.0.2
pandas==0.24.1
requests_oauthlib==1.2.0
numpy==1.13.3
```

Alternatively, you can run 
```
$ pip install -r requirements.txt
```

To run the tool use
```
python freesounds_scraper.py
```

By default, it expects you to have a csv file named `query.csv` of the queries that you want to make in the following format:
```
<query>,<number of samples to retrieve>
```

