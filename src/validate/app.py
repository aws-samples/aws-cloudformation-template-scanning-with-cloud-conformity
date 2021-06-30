# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json
import boto3
import requests
import os
import traceback
import logging
from botocore.exceptions import ClientError
from typing import Any, Dict, List
from validate import exceptions

logger = logging.getLogger("templateScanner")
logger.setLevel(logging.DEBUG)

# Failing checks in this list will be returned.
FAILURE_FILTER = ["VERY_HIGH", "HIGH", "MEDIUM", "LOW"]

# Set in global scope at end of file to allow caching between invocations
API_KEY = ''
ACCOUNTS_LIST = []


def populate_api_key():
    """
    Fetches the CloudConformity API key from Secrets Manager and populates the
    global var API_KEY.
    :return:
    """
    logger.info('populate_api_key()')
    global API_KEY

    region_name = os.environ['AWS_REGION']
    stage = os.environ['STAGE']
    secret_name = "template-validator/" + stage

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    secret = ''
    try:
        logger.debug(f'Looking for API key in Secrets Manager at {secret_name}')
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name)

    except ClientError as e:
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])

    try:
        logger.debug('got secret, setting API_KEY...')
        API_KEY = json.loads(secret)["api-key"]
        return API_KEY

    except TypeError:
        raise TypeError('"api-key" missing from Secrets Manager, this needs to be set to CloudConformity API key"')


def get_cloud_conformity_headers() -> Dict[str, str]:
    """
    Returns the request headers required to call CloudConformity APIs
    Importantly sets the Authorization header with the API key
    :return: JSON header object as Dict
    """
    logger.info('get_cloud_conformity_headers()')

    global API_KEY
    if (API_KEY == ''):
        logger.debug('API_KEY empty, getting new value')
        populate_api_key()

    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': 'ApiKey ' + API_KEY
    }
    return headers


def get_scan_result(payload: Dict[str, Any]) -> Any:
    """
    Calls the CloudConformity Template Scanner API with 'payload'
    :param payload: JSON object as defined in https://cloudone.trendmicro.com/docs/conformity/api-reference/tag/Template-scanner
    :return: requests.Response object (https://docs.python-requests.org/en/latest/api/#requests.Response)
             Actual results from CloudConformity API call are in respone.text
    """
    logger.info('get_scan_result - request payload:\n' + json.dumps(payload, indent=2))
    resp: Any = ''
    try:
        region_name = os.environ['AWS_REGION']
        template_scanner_url = f'https://{region_name}-api.cloudconformity.com/v1/template-scanner/scan'
        resp = requests.post(template_scanner_url, data=json.dumps(payload), headers=get_cloud_conformity_headers())
        logger.debug('get_scan_result - response:\n' + resp.text + "\n\n")
    except Exception:
        logger.error("Exception occurred in get_scan_result! " + traceback.format_exc())

    return resp


def populate_accounts_list() -> None:
    """
    Makes a call to CloudConformity accounts API (https://cloudone.trendmicro.com/docs/conformity/api-reference/tag/Accounts)
    to obtain a list of account data. Inside which there is a mapping of Cloud Conformity account number to AWS account number
    This function populates the global var ACCOUNTS_LIST
    :returns:
    """
    logger.info('populate_accounts_list()')
    try:
        global ACCOUNTS_LIST
        region_name = os.environ['AWS_REGION']
        accountsUrl = f'https://{region_name}-api.cloudconformity.com/v1/accounts'

        resp = requests.get(accountsUrl,
                            headers=get_cloud_conformity_headers())
        logger.debug('Accounts Response:\n' + resp.text + '\n\n')

        if (resp.status_code != 200):
            resp.raise_for_status()

        respObj = json.loads(resp.text)

        ACCOUNTS_LIST.clear()
        ACCOUNTS_LIST = respObj["data"]

        logger.debug(f'respObj["data"] size: {len(respObj["data"])}')
        logger.debug(f'ACCOUNTS_LIST size: {len(ACCOUNTS_LIST)}')

    except Exception as e:
        logger.debug("Exception occurred in populate_accounts_list! " + traceback.format_exc())
        raise e


def search_accounts(awsAccount: str) -> str:
    """
    Given an AWS account number, this function looks up the corresponding CloudConformity account number
    using the global var ACCOUNTS_LIST.
    :returns: CloudConformity account number (as string), or empty string if not found.
    """
    logger.info(f'search_accounts({awsAccount})')

    for entry in ACCOUNTS_LIST:
        if entry['attributes']['awsaccount-id'] == awsAccount:
            logger.debug(f'Found CC account {entry["id"]} for AWS account {awsAccount}')
            return str(entry['id'])

    return ''


def get_account(awsAccount: str) -> str:
    """
    Searches global ACCOUNTS_LIST for AWS Account ID, returning CloudConformity account ID if
    present. If ACCOUNTS_LIST is empty, will make call to populate from CloudConformity.
    """
    logger.info(f'get_account({awsAccount})')
    try:
        conformity_id = ''

        # first time call, populate global var to cache for next time
        if (len(ACCOUNTS_LIST) == 0):
            populate_accounts_list()

        conformity_id = search_accounts(awsAccount)
        if (conformity_id == ''):
            logger.debug('Did not find AWS account id. Account data maybe stale, refreshing...')
            populate_accounts_list()
            conformity_id = search_accounts(awsAccount)

        return conformity_id

    except Exception as e:
        logger.debug("Exception occurred in get_account! " + traceback.format_exc())
        raise e


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any], dynamodb=None) -> Dict[str, Any]:
    """
    Entry point for Validate API.
    Expects a POST payload in event. Sends all templates through the CloudConformity Template Scanner API,
    and returns checks in Cucumber JSON format (readable by CodeBuild reports)
    :param event: Expected in the form: event['body'] =
        {
            "accountId": "<AWS account id from caller>",
            "templates": [
                {
                "filename" : "mytemplate.yml",
                "template": "<stringified cloudformation template>",
                },
                ...
            ]
        }
    :param context: not used
    :param dynamodb: Pass in for unit testing, otherwise None will mean dynamodb resource will be created
    :returns:
        {
            "statusCode": "[200|500]",
            "body": {
                "failures": {
                    "VERY_HIGH": 12,
                    "HIGH": 2,
                    "MEDIUM": 2,
                    "LOW": 6
                },
                "results" : "<cucumber JSON with validate results>"
            }
        }
    """
    try:
        logger.info("lambda_handler(event): " + json.dumps(event, indent=2))

        body = json.loads(event['body'], strict=False)

        # List of HIGH-RISK failures
        failuresList: Dict[str, Any] = {}
        filename: str = ''

        cc_account_id: str = ''
        cc_account_id = extract_account(body, failuresList)

        exceptionList: Dict[str, Any] = {}
        if ('accountId' in body):
            exceptionList = exceptions.get_approved_exceptions(body["accountId"], dynamodb)

        templates: List[Dict[str, Any]] = body['templates']
        for entry in templates:
            if ('filename' in entry):
                filename = entry['filename']
            scan_template(filename, failuresList, cc_account_id, entry['template'], exceptionList)

        # get the results in order (highest sev first)
        results = []
        failuresCount = {
            "VERY_HIGH": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }

        for riskLevel in reversed(list(failuresList.keys())):
            for check in failuresList[riskLevel]['elements']:
                if (check['steps'][0]['result']['status'] == "failed"):
                    failuresCount[riskLevel] += 1
            results.append(failuresList[riskLevel])

        logger.debug('failuresCount: ' + json.dumps(failuresCount, indent=2))

        cucumberResults = json.dumps(results)

        logger.debug(f'Results converted to Cucumber: {cucumberResults}')

        return_response = {
            "statusCode": 200,
            "body": json.dumps({'failures': failuresCount, 'results': cucumberResults})
        }
        logger.debug(f'return_response: {json.dumps(return_response, indent=2)}')

        return return_response

    except json.decoder.JSONDecodeError:
        logger.error("JSONDecodeError occurred in lambda_handler! " + traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Invalid JSON provided in request'})
        }
    except TypeError as e:
        logger.error("Malformed request payload, missing elements")
        logger.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Malformed request body, missing elements: {e}'})
        }
    except Exception:
        status_code = 500
        logger.error("Exception occurred in lambda_handler! " + traceback.format_exc())
        return {
            'statusCode': status_code,
            'body': json.dumps({'message': traceback.format_exc()})
        }


def extract_account(body: Dict[str, Any], failuresList: Dict[str, Any]) -> str:
    ccAccount: str = ''
    if ('accountId' in body):
        accountId = body['accountId']
        ccAccount = get_account(accountId)
        if ccAccount == '':
            addTestResult('cloud-conformity-tests',
                          'AWS account number validation', 'VERY_HIGH',
                          f'AWS account {accountId} is NOT being monitored by Cloud Conformity',
                          '', 'failed', failuresList)
    else:
        addTestResult('cloud-conformity-tests',
                      'AWS account number validation',
                      'VERY_HIGH', 'AWS account number not provided as accountID in POST body to validate API',
                      '', 'failed', failuresList)

    return ccAccount


def scan_template(filename: str, failuresList, cc_account_id: str, cfn_template: str, exceptionList: Dict[str, Any]) -> None:

    payload = {
        'data': {
            'attributes': {
                'type': 'cloudformation-template',
                'contents': cfn_template
            }
        }
    }

    if (cc_account_id != ''):
        payload['data']['attributes']['account'] = cc_account_id
    else:
        logger.warning('No valid, monitored, AWS account ID provided - using default CloudConformity rules')

    resp = get_scan_result(payload)
    if (resp.status_code != 200):
        errors = json.loads(resp.text)
        logger.debug(f'error: {errors}')
        details = errors['errors'][0]['detail']
        addTestResult('cloud-conformity-tests',
                      'CloudConformity Response Error', 'VERY_HIGH',
                      f'CloudConformity replied with {resp.status_code} error: {details}',
                      filename, 'failed', failuresList)
    processScanResults(resp.text, filename, failuresList, exceptionList)


def convertStatus(status: str) -> str:
    if (status == 'SUCCESS'):
        return 'passed'
    elif (status == 'FAILURE'):
        return 'failed'
    else:
        return status


def processScanResults(ccResults: str, filename: str, tests: Dict[str, Any], exceptionList: Dict[str, Any]) -> None:
    logger.info('processScanResults')
    try:
        resultsObj = json.loads(ccResults)

        for check in resultsObj["data"]:
            ruleId = check['relationships']['rule']['data']['id']
            message = check['attributes']['message']
            status = check['attributes']['status']
            # Check to see if any failed checks are OK because on exception list
            if (f'{filename}#{ruleId}' in exceptionList):
                rule = check['attributes']['message']
                logger.debug(f'Rule {rule} passed as there is an approved exception')
                status = 'skipped'

            addTestResult(check['id'],
                          check['attributes']['rule-title'],
                          check['attributes']['risk-level'],
                          f'{ruleId}: {message}',
                          filename,
                          status,
                          tests)

        # If 'tests' is empty means we are good to go
        if (len(tests) == 0):
            logger.debug(
                f'No issues added to the list - therefore file {filename} has PASSED')
            addTestResult('cloud-conformity-tests',
                          'Template Scanning',
                          'PASSED',
                          'template scan found ZERO issues',
                          filename,
                          'passed',
                          tests)

    except Exception:
        logger.debug("Could not convert results to cucumber format! " + traceback.format_exc())


def addTestResult(
        id: str,
        ruleTitle: str,
        riskLevel: str,
        message: str,
        filename: str,
        status: str,
        resultsArray: Dict[str, Any]):
    logger.debug(f'Adding test {status} with message: {message}')

    status = convertStatus(status)

    # TODO add error handling
    if (riskLevel in FAILURE_FILTER or riskLevel == "PASSED" or riskLevel == "EXEMPTED"):

        if riskLevel not in resultsArray:
            resultsArray[riskLevel] = {
                "id": "cloud-conformity-rules",
                "description": "Results from scanning templates through Cloud Conformity",
                "name": riskLevel,
                "elements": []
            }

        failedCheck = {
            "id": id,
            "name": ruleTitle,
            "steps": [
                {
                    "result": {
                        "status": status
                    },
                    "name": message,
                    "keyword": f'{filename}: '
                }
            ]
        }

        resultsArray[riskLevel]['elements'].append(failedCheck)

    else:
        logger.debug(
            f'Test result was ignored because risk level is {riskLevel}')
