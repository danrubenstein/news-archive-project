''' 
Script / function to download json files and transform into a dataframe
'''

import argparse
import boto3
import configparser
import datetime
import json
import logging
import os
import pandas as pd 
import shutil
import subprocess
import time
import uuid


def download_files(temporary_output_directory, force_update=True):
	'''
	Download the files from the s3 bucket
	'''
	if force_update or len([x for x in os.listdir() if "tmp-resource" in x]) == 0:
		clean_temporary_resources()
		os.mkdir(temporary_output_directory)
		aws_cmd = "aws s3 cp --recursive s3://news-archive-project/newsapi-json ./{}".format(temporary_output_directory).split()
		subprocess.call(aws_cmd)
		source_strip_cmd = "rm ./{}/sources.json".format(temporary_output_directory).split()
		subprocess.call(source_strip_cmd)


def get_json_as_dataframe(json_directory):
	'''
	Transform the json into a pandas dataframe

	Returns that dataframe
	'''
	jsonfiles = [f for f in os.listdir(json_directory) if os.path.isfile(os.path.join(json_directory, f))]

	dataframes = []

	for file in jsonfiles:

		loaded_json = json.load(open(os.path.join(json_directory, file)))
		dataframe = pd.DataFrame(loaded_json["articles"])
		dataframe["time_fetch"] = datetime.datetime.fromtimestamp(loaded_json["time"])
		dataframes.append(dataframe)

	return pd.concat(dataframes)


def clean_temporary_resources():
	''' 
	Deletes all temporary folder files
	'''
	resource_directories = [x for x in os.listdir() if "tmp-resource" in x and os.path.isdir(x)]
	for dir in resource_directories:
		shutil.rmtree(dir)


def load_resources(update=False):
	
	'''
	Load resources, by downloading if necessary
	'''

	if update:
		raw_directory = "tmp-resource-"+str(uuid.uuid4())
		download_files(raw_directory, force_update=update)
		articles_df = get_json_as_dataframe(raw_directory)

	else:
		resource_directories = [x for x in os.listdir() if "tmp-resource" in x]
		if len(resource_directories) == 1:
			articles_df = get_json_as_dataframe(resource_directories[0])
		else:
			print("I'm sorry, but there are no available resource directories.")


if __name__ == "__main__":

	load_resources(update=True)


