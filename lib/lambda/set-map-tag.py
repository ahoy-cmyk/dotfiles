from __future__ import print_function
import json
import boto3
import logging
import time
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)
                                
def handler(event, context):
    #logger.info('Event: ' + str(event))
    #print('Received event: ' + json.dumps(event, indent=2))
    ids = []
    try:
        region = event['region']
        detail = event['detail']
        eventname = detail['eventName']
        arn = detail['userIdentity']['arn']
        principal = detail['userIdentity']['principalId']
        userType = detail['userIdentity']['type']
            
        if userType == 'IAMUser':
            user = detail['userIdentity']['userName']
                                
        else:
            user = principal.split(':')[1]
                                
                            
        logger.info('principalId: ' + str(principal))
        logger.info('region: ' + str(region))
        logger.info('eventName: ' + str(eventname))
        logger.info('detail: ' + str(detail))
                                  
        if not detail['responseElements']:
            logger.warning('Not responseElements found')
            if detail['errorCode']:
                logger.error('errorCode: ' + detail['errorCode'])
            if detail['errorMessage']:
                logger.error('errorMessage: ' + detail['errorMessage'])
            return False

        ec2 = boto3.resource('ec2')
                                
        if eventname == 'RunInstances':
            items = detail['responseElements']['instancesSet']['items']
            for item in items:
                ids.append(item['instanceId'])
            logger.info('number of instances: ' + str(len(ids)))

    
        else:
            logger.warning('Not supported action')
                        
        if ids:
            for resourceid in ids:
                print('Tagging resource ' + resourceid)
            logger.info('ID Information:'+str(ids))
            ec2.create_tags(Resources=ids, Tags=[{'Key': 'Owner', 'Value': user}, {'Key': 'PrincipalId', 'Value': principal}, {'Key': 'map-migrated', 'Value': 'arrington-142'}])
        
        logger.info(' Remaining time (ms): ' + str(context.get_remaining_time_in_millis()) + '\\n')
        return True
        
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return False
                        