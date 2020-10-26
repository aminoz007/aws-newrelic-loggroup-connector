"""
Copyright 2017 New Relic, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This Lambda function is used to automatically subscribe newly created 
and existing Cloudwatch LogGroups to NR logs ingestion lambda.
"""

import boto3
import os

LOG_GROUP_TAGS = os.getenv("LOG_GROUP_TAGS", "")
LOG_GROUP_PATTERN = os.getenv("LOG_GROUP_PATTERN","")
LAMBDA_ARN = os.getenv("LAMBDA_ARN","")
USE_EXISTING_LOG_GROUPS = os.getenv("USE_EXISTING_LOG_GROUPS", "false")

client = boto3.client('logs')

def subscribeToLogIngestionFunction(logGroupName):
    try:
        response = client.put_subscription_filter(
            logGroupName=logGroupName,
            filterName='NewRelicLGFilter',
            filterPattern='',
            destinationArn=LAMBDA_ARN
        )
    except Exception as e:
        print(f'Error subscribing: {logGroupName} => {e}')

def filterLogGroups(logGroups, pattern, tags):
    filterdGroups = []
    for logGroup in logGroups:
        if pattern.match(logGroup['logGroupName']) & (logGroup['eventName'] == 'existingLogs' | logGroup['eventName'] == 'CreateLogGroup'):
            filteredGroups.append(logGroup['logGroupName'])
            continue
        if tags & logGroup['tags']:
            for tag in tags:
                tagArray = tag.split("=")
                key = tagArray[0].trim()
                value = tagArray[1].trim()
                if (key, value) in logGroup['tags'].items():
                    filteredGroups.append(logGroup['logGroupName'])
                    break
    return filterdGroups

def getExistingLogGroups(token, logGroups):
    try:
        response = client.describe_log_groups(
            nextToken='',
            limit=40
        )
        for logGroup in response['logGroups']:
            logGroups.push({'logGroupName':logGroup['logGroupName'], 'tags':'', 'eventName':'existingLogs'}) # describe logs API doesn't offer a way to get tags for existing logs
        if response['nextToken']: 
            getExistingLogGroups(response['nextToken'], logGroups)
        return logGroups
    except Exception as e:
        print(f'Error fetching logGroups => {e}')


def lambda_handler(event, context):
    """
    This is the Lambda handler, which is called when the function is invoked.
    Changing the name of this function will require changes in Lambda
    function's configuration.
    """

    print("Starting Log Connector Function")

    if (USE_EXISTING_LOG_GROUPS == 'false'):
        logGroups = [({'logGroupName': event['detail']['requestParameters']['logGroupName'],
                       'tags':event['detail']['requestParameters']['tags'], 'eventName':event['detail']['eventName']})]
    else:
        logGroups = getExistingLogGroups(null, [])
    
    pattern = re.compile(LOG_GROUP_PATTERN)
    tags = LOG_GROUP_TAGS.split(",")

    logGroupNames = filterLogGroups(logGroups, pattern, tags)
    if logGroupNames:
        for name in logGroupNames:
            subscribeToLogIngestionFunction(name)

    # This makes it possible to chain this CW log consumer with others using a success destination
    return event

