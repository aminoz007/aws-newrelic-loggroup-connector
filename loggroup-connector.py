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

"""
Author: Amine Benzaied (Expert Services)
"""

import boto3
import os
import re

LOG_GROUP_TAGS = os.getenv("LOG_GROUP_TAGS", "")
LOG_GROUP_PATTERN = os.getenv("LOG_GROUP_PATTERN", "")
LAMBDA_ARN = os.getenv("LAMBDA_ARN", "")
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
        print(f'Subscribed logGroup: {logGroupName}')
    except Exception as e:
        print(f'Error subscribing: {logGroupName} => {e}')


def filterLogGroups(logGroups, pattern, tags):
    filteredGroups = []
    for logGroup in logGroups:
        if pattern.search(logGroup.get('logGroupName')) and (logGroup.get('eventName') == 'existingLogs' or logGroup.get('eventName') == 'CreateLogGroup'):
            filteredGroups.append(logGroup.get('logGroupName'))
            continue
        if tags and logGroup.get('tags'):
            for tag in tags:
                tagArray = tag.split("=")
                key = tagArray[0].strip()
                value = tagArray[1].strip()
                if (key, value) in logGroup.get('tags').items():
                    filteredGroups.append(logGroup.get('logGroupName'))
                    break
    return filteredGroups


def getExistingLogGroups(token, logGroups):
    try:
        print('Fetching existing logGroups')
        if token:
            response = client.describe_log_groups(
                nextToken=token
            )
        else: 
            response = client.describe_log_groups()
        for logGroup in response.get('logGroups'):
            # describe logs API doesn't offer a way to get tags for existing logs
            logGroups.append({'logGroupName': logGroup.get(
                'logGroupName'), 'tags': '', 'eventName': 'existingLogs'})
        if response.get('nextToken'):
            getExistingLogGroups(response.get('nextToken'), logGroups)
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
        logGroups = [({'logGroupName': event.get('detail').get('requestParameters').get('logGroupName'),
                       'tags': event.get('detail').get('requestParameters').get('tags'), 'eventName': event.get('detail').get('eventName')})]
    else:
        logGroups = getExistingLogGroups(None, [])

    pattern = re.compile(LOG_GROUP_PATTERN)
    tags = LOG_GROUP_TAGS.split(",")

    logGroupNames = filterLogGroups(logGroups, pattern, tags)
    if logGroupNames:
        for name in logGroupNames:
            subscribeToLogIngestionFunction(name)
    else:
        print("Nothing matching your rules")
    print("Ending Log Connector Function")

    # This makes it possible to chain this CW log consumer with others using a success destination
    return event
