import requests
import json
import datetime
import config
import csv

#information for API call
url = "https://app.pendo.io/api/v1/feature"
headers = {
    'x-pendo-integration-key': config.pendo_key,
    'content-type': "application/json"
}

response = requests.get(url, headers = headers)
response_dictionary = json.loads(response.content)
with open('features.csv', 'w') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(["feature", "name"])
	for i in range(len(response_dictionary)):
		writer.writerow([response_dictionary[i]["id"], response_dictionary[i]["name"]])