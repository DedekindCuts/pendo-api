import requests
import json
import datetime
import pymysql.cursors
import config

#make sure to edit the file "config.py" to include your MySQL database connection information and your Pendo API key

#information for Pendo API
url = "https://app.pendo.io/api/v1/aggregation"
headers = {
    'x-pendo-integration-key': config.pendo_key,
    'content-type': "application/json"
}

#connect to the MySQL database
connection = pymysql.connect(host='localhost',
                             user=config.user,
                             password=config.password,
                             db='Pendo',
                             cursorclass=pymysql.cursors.DictCursor)

sources = ["featureEvents", "guideEvents", "pageEvents", "pollEvents"]
days_ago_count = XXX

#pull and write for each source for each day since days_ago_count days ago
for j in range(days_ago_count):
	for source_name in sources:
		data = "{\"response\":{\"mimeType\":\"application/json\"},\"request\":{\"pipeline\":[{\"source\":{\"" + source_name + "\":null,\"timeSeries\":{\"first\":\"now()-" + str(j + 1) + "*24*60*60*1000\",\"count\":1,\"period\":\"dayRange\"}}}]}}"

		#retrieve data from Pendo
		response = requests.post(url, data = data, headers = headers)
		response_dictionary = json.loads(response.content)

		#check for error in retrieving data and check if response is empty
		print(source_name, j + 1, "day(s) ago :", response)
		if(response_dictionary['results'] is not None):
			#convert ms timestamps
			if(source_name in ["featureEvents", "pageEvents"]):
				for i in range(len(response_dictionary['results'])):
					response_dictionary['results'][i]['day'] = datetime.datetime.fromtimestamp((response_dictionary['results'][i]['day'])/1000.0)
			elif(source_name in ["guideEvents", "pollEvents"]):
				for i in range(len(response_dictionary['results'])):
					response_dictionary['results'][i]['browserTime'] = datetime.datetime.fromtimestamp((response_dictionary['results'][i]['browserTime'])/1000.0)
			else:
				print("Warning: Timestamps not converted")

			#try to write to the appropriate MySQL table
			try:
				cursor = connection.cursor()
				if(source_name == "featureEvents"):
					sql = "INSERT INTO `feature_events` (`accountId`,`visitorId`,`numEvents`,`numMinutes`,`server`,`remoteIp`,`parameters`,`userAgent`,`day`,`appId`,`featureId`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
					for i in range(len(response_dictionary['results'])):
						cursor.execute(sql,(response_dictionary['results'][i]['accountId'],response_dictionary['results'][i]['visitorId'],response_dictionary['results'][i]['numEvents'],response_dictionary['results'][i]['numMinutes'],response_dictionary['results'][i]['server'],response_dictionary['results'][i]['remoteIp'],response_dictionary['results'][i]['parameters'],response_dictionary['results'][i]['userAgent'],response_dictionary['results'][i]['day'],response_dictionary['results'][i]['appId'],response_dictionary['results'][i]['featureId']))
				elif(source_name == "guideEvents"):
					sql = "INSERT INTO `guide_events` (`accountIds`,`browserTime`,`country`,`elementPath`,`eventId`,`type`,`guideId`,`guideStepId`,`latitude`,`loadTime`,`longitude`,`region`,`remoteIp`,`serverName`,`url`,`userAgent`,`visitorId`,`accountId`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
					for i in range(len(response_dictionary['results'])):
						cursor.execute(sql,(response_dictionary['results'][i]['accountIds'],response_dictionary['results'][i]['browserTime'],response_dictionary['results'][i]['country'],response_dictionary['results'][i]['elementPath'],response_dictionary['results'][i]['eventId'],response_dictionary['results'][i]['type'],response_dictionary['results'][i]['guideId'],response_dictionary['results'][i]['guideStepId'],response_dictionary['results'][i]['latitude'],response_dictionary['results'][i]['loadTime'],response_dictionary['results'][i]['longitude'],response_dictionary['results'][i]['region'],response_dictionary['results'][i]['remoteIp'],response_dictionary['results'][i]['serverName'],response_dictionary['results'][i]['url'],response_dictionary['results'][i]['userAgent'],response_dictionary['results'][i]['visitorId'],response_dictionary['results'][i]['accountId']))
				elif(source_name == "pageEvents"):
					sql = "INSERT INTO `page_events` (`accountId`,`visitorId`,`numEvents`,`numMinutes`,`server`,`remoteIp`,`parameters`,`userAgent`,`day`,`appId`,`pageId`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
					for i in range(len(response_dictionary['results'])):
						cursor.execute(sql,(response_dictionary['results'][i]['accountId'],response_dictionary['results'][i]['visitorId'],response_dictionary['results'][i]['numEvents'],response_dictionary['results'][i]['numMinutes'],response_dictionary['results'][i]['server'],response_dictionary['results'][i]['remoteIp'],response_dictionary['results'][i]['parameters'],response_dictionary['results'][i]['userAgent'],response_dictionary['results'][i]['day'],response_dictionary['results'][i]['appId'],response_dictionary['results'][i]['pageId']))
				elif(source_name == "pollEvents"):
					sql = "INSERT INTO `poll_events` (`accountIds`,`browserTime`,`country`,`elementPath`,`eventId`,`type`,`guideId`,`guideStepId`,`latitude`,`loadTime`,`longitude`,`pollId`,`region`,`remoteIp`,`serverName`,`url`,`userAgent`,`visitorId`,`accountId`,`pollResponse`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
					for i in range(len(response_dictionary['results'])):
						cursor.execute(sql,(response_dictionary['results'][i]['accountIds'],response_dictionary['results'][i]['browserTime'],response_dictionary['results'][i]['country'],response_dictionary['results'][i]['elementPath'],response_dictionary['results'][i]['eventId'],response_dictionary['results'][i]['type'],response_dictionary['results'][i]['guideId'],response_dictionary['results'][i]['guideStepId'],response_dictionary['results'][i]['latitude'],response_dictionary['results'][i]['loadTime'],response_dictionary['results'][i]['longitude'],response_dictionary['results'][i]['pollId'],response_dictionary['results'][i]['region'],response_dictionary['results'][i]['remoteIp'],response_dictionary['results'][i]['serverName'],response_dictionary['results'][i]['url'],response_dictionary['results'][i]['userAgent'],response_dictionary['results'][i]['visitorId'],response_dictionary['results'][i]['accountId'],response_dictionary['results'][i]['pollResponse']))
				else:
					print("Error: Source not recognized")
				connection.commit()
				print(source_name, "written successfully")
			except:
				print("Error: Could not write to MySQL table")
		else:
			print("Response is empty")

#close the connection
connection.close()