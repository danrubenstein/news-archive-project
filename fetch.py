'''
Script to support the fetching of data
'''

import argparse
import boto3
import configparser
import datetime
import json
import logging
import os
import requests
import time


def initialize_sources(filename):
    '''
    Loads raw json from sources and returns relevant stuff
    '''
    json_sources = json.load(open(filename, 'r'))['sources']
    source_keys = ['category', 'id', 'sortBysAvailable', 'name']
    sources_formatted = []

    for source in json_sources:
        if dict(source)["language"] == "en":
            source_formatted = dict((key, dict(source)[key]) for key in source_keys)
            sources_formatted.append(source_formatted)

    return sources_formatted


def get_result_from_source(source_dict, API_key):
    '''
    Runs a request...

    Parameters:
        source_dict - source information (probably from sources.json)

    Returns:
        the articles from that source (list of dicts)
    '''

    newsapi_url = "https://newsapi.org/v1/articles"
    newsapi_paramters = {
        "source" : source_dict["id"],
        "apiKey" : API_key,
        "sortby" : source_dict["sortBysAvailable"][0]
    }
    req = requests.get(newsapi_url, params=newsapi_paramters)
    logger = logging.getLogger('logs')

    if req.status_code != 200:
        logger.debug("Return code from news api: {}".format(req.status_code))
        logger.debug("Return text from news api: {}".format(req.text))
        return None

    article_keys = ['url', 'title', 'description']
    articles_formatted = []

    for article in req.json()['articles']:
        article_formatted = dict((key, dict(article)[key]) for key in article_keys)
        article_formatted['source'] = source_dict["id"]
        article_formatted['dt_fetched'] = str(datetime.datetime.utcnow())
        articles_formatted.append(article_formatted)

    return articles_formatted


def handler(event, context):

    client = boto3.client('s3')
    client.download_file('news-archive-project', 'newsapi-json/sources.json', '/tmp/sources.json')

    sources = initialize_sources("/tmp/sources.json")

    article_results = []

    for source in sources:
        source_results = get_result_from_source(source, os.environ['NEWS_API_KEY'])
        if source_results is not None:
            article_results += source_results

    output_file_name = "-".join(str(datetime.datetime.now()).split()) + "_output.json"
    output_file_path = "/tmp/" + output_file_name
    output_file = open(output_file_path, 'w')
    
    output = {
        'time' : time.time(),
        'articles' : article_results
    }
    output_file.write(json.dumps(output))
    
    # AWS upload
    client.upload_file(output_file_path, 'news-archive-project', 'newsapi-json/{}'.format(output_file_name))



    