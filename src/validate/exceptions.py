# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json
import boto3
import traceback
import logging
import os
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from typing import Any, Dict
logger = logging.getLogger("TemplateScannerExceptions")
logger.setLevel(logging.DEBUG)


def request(event: Dict[str, Any], context: Dict[str, Any], dynamodb=None) -> Dict[str, Any]:
    """
    User can request exceptions so that CloudConformity checks matching the rule IDs will not
    be counted as part of failed checks when using the validate API. Multiple rules can be requested 
    by providing a list of request entries in event

    :param event: We expect it in the form: event['body'] = [
        {"awsAccountId": 0123456789012,
         "filename": "mycfntemplate.yml",
         "ruleId": "<CloudConformityRuleId>",
         "requestReason": "<string of why rule is being exempted for this file",
         "requestedBy": "<requester name>"
        },
        ...
    ]

    :param context: not used
    :param dynamodb: Pass in for unit testing, otherwise None will mean dynamodb resource will be created
    :return: 201 if successful. 500 if any error encountered
    """

    statusCode = 500
    message = ''
    try:
        logger.info("request(event): " + json.dumps(event, indent=2))

        if (dynamodb is None):
            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ.get('EXCEPTIONS_TABLENAME'))

        # loop through list of exception requests, add to table
        with table.batch_writer() as batch:
            for req in json.loads(event['body']):
                item = {
                    'partKey': req["awsAccountId"],
                    'sortKey': f'{req["filename"]}#{req["ruleId"]}',
                    'awsAccountId': req["awsAccountId"],
                    'filename': req["filename"],
                    'ruleId': req["ruleId"],
                    'requestReason': req["requestReason"],
                    'requestedBy': req["requestedBy"]
                }
                batch.put_item(Item=item)

        logger.info('Successfully added requests')
        statusCode = 201

    except ClientError as e:
        message = f'Error adding exception to table: {e.response["Error"]["Message"]}'
        logger.error(message)
    except TypeError as e:
        logger.error("Malformed request body, missing element in json")
        logger.error(traceback.format_exc())
        message = f'Malformed request payload, missing elements: {e}'
    except Exception:
        logger.error("Exception occurred in lambda_handler! " + traceback.format_exc())
        message = traceback.format_exc()

    return {
        'statusCode': statusCode,
        'body': json.dumps({'message': message})
    }


def approve(event: Dict[str, Any], context: Dict[str, Any], dynamodb=None) -> Dict[str, Any]:
    """
    Approve an already existing request
    :param event: We expect it in the form: event['body'] = [
        {"awsAccountId": 0123456789012,
         "filename": "mycfntemplate.yml",
         "ruleId": "<CloudConformityRuleId>",
         "approvedBy": "<the approver of the request"
        }
    :param context: not used
    :param dynamodb: Pass in for unit testing, otherwise None will mean dynamodb resource will be created
    :return: 201 if successful. 500 if no matching request found, or other general error encountered
    """
    statusCode = 500
    message = ''
    try:
        logger.info("approve(event): " + json.dumps(event, indent=2))

        if (dynamodb is None):
            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ.get('EXCEPTIONS_TABLENAME'))

        req = json.loads(event['body'])
        sortKey = f'{req["filename"]}#{req["ruleId"]}'
        logger.debug(f'approving item with partKey: {req["awsAccountId"]} sortKey: {sortKey}')
        table.update_item(
            Key={"partKey": req["awsAccountId"], "sortKey": sortKey},
            ConditionExpression=Attr('partKey').eq(req["awsAccountId"]) & Attr('sortKey').eq(sortKey),
            UpdateExpression="set approved = :approved, approvedBy = :approvedBy",
            ExpressionAttributeValues={
                    ':approved': "true",
                    ':approvedBy': req["approvedBy"]
                },
            ReturnValues="UPDATED_NEW"
        )

        logger.info('Successfully approved request for {req["awsAccountId"]} sortKey: {sortKey}')
        statusCode = 201

    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        message = 'No matching request found to approve'
        logger.warning(message)
    except ClientError as e:
        message = f'Error adding exception to table: {e.response["Error"]["Message"]}'
        logger.error(message)
        raise e
    except TypeError as e:
        logger.error("Malformed request body, missing element in json")
        logger.error(traceback.format_exc())
        message = f'Malformed request payload, missing elements: {e}'
    except Exception:
        logger.error("Exception occurred in lambda_handler! " + traceback.format_exc())
        message = traceback.format_exc()

    return {
        'statusCode': statusCode,
        'body': json.dumps({'message': message})
    }


def delete(event: Dict[str, Any], context: Dict[str, Any], dynamodb=None) -> Dict[str, Any]:
    """
    Delete an exception request (approved or not). 
    :param event: We expect it in the form: event['body'] = [
        {"awsAccountId": 0123456789012,
         "filename": "mycfntemplate.yml",
         "ruleId": "<CloudConformityRuleId>"
        }
    :param context: not used
    :param dynamodb: Pass in for unit testing, otherwise None will mean dynamodb resource will be created
    :return: 200 if delete successful. 500 if no matching request found, or other general error encountered
    """
    statusCode = 500
    message = ''
    try:
        logger.info("approve(event): " + json.dumps(event, indent=2))

        if (dynamodb is None):
            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ.get('EXCEPTIONS_TABLENAME'))

        req = json.loads(event['body'])
        sortKey = f'{req["filename"]}#{req["ruleId"]}'
        logger.debug(f'approving item with partKey: {req["awsAccountId"]} sortKey: {sortKey}')
        table.delete_item(
            Key={"partKey": req["awsAccountId"], "sortKey": sortKey}
        )

        logger.info('Successfully removed exception for {req["awsAccountId"]} sortKey: {sortKey}')
        statusCode = 200

    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        message = 'No matching request found to approve'
        logger.warning(message)
    except ClientError as e:
        message = f'Error adding exception to table: {e.response["Error"]["Message"]}'
        logger.error(message)
        raise e
    except TypeError as e:
        logger.error("Malformed request body, missing element in json")
        logger.error(traceback.format_exc())
        message = f'Malformed request payload, missing elements: {e}'
    except Exception:
        logger.error("Exception occurred in lambda_handler! " + traceback.format_exc())
        message = traceback.format_exc()

    return {
        'statusCode': statusCode,
        'body': json.dumps({'message': message})
    }


# where key = <filename>#<ruleId> value = <exception entry>
def get_approved_exceptions(awsAccountId: str, dynamodb: Any = None) -> Dict[str, Any]:
    """
    Get a dictionary for all approved exceptions for the given AWS account number.
    This is used internally in the Validate API, to omit any failed checks from
    the reports.
    :param awsAccountId: AWS account number, eg. 0123456789012
    :param dynamodb: Pass in for unit testing, otherwise None will mean dynamodb resource will be created
    :return: dictionary where key = <filename>#<ruleId> value = <exception entry>
    """
    exceptionDict = {}
    try:
        logger.info(f'get_approved_exceptions({awsAccountId})')
        if (dynamodb is None):
            dynamodb = boto3.resource('dynamodb', os.environ['AWS_REGION'])

        table = dynamodb.Table(os.environ.get('EXCEPTIONS_TABLENAME'))
        response = table.query(
            KeyConditionExpression=Key('partKey').eq(awsAccountId)
        )

        logger.debug(f'Raw table dump for account {awsAccountId}:\n {response["Items"]}')

        for ex in response['Items']:
            # sortKey is in format: <filename>#<ruleId>
            try:
                if (ex['approved'] == 'true'):
                    exceptionDict[ex['sortKey']] = ex
                    logger.debug(f'approved exception: {ex["sortKey"]}')
            except TypeError:
                continue  # the exception request is not approved

        logger.debug(f'exception list for account {awsAccountId}:\n {response["Items"]}')

    except Exception:
        logger.warning("Exception occurred whilst retrieving approved exceptions: " + traceback.format_exc())

    logger.info(f'get_approved_exceptions(): Approved exception list for {awsAccountId}: {exceptionDict.keys()}')

    return exceptionDict
