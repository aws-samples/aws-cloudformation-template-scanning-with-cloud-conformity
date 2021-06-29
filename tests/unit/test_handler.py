# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json
import os
from requests import HTTPError
import requests_mock
import boto3
from moto import mock_secretsmanager, mock_dynamodb2
from unittest import mock
from unittest import TestCase

from validate import app
import tests.unit.helpers as helpers


@mock_secretsmanager
def invoke_validate_handler(event, dynamodb):
    mock_env = mock.patch.dict(os.environ, {"EXCEPTIONS_TABLENAME": "TEST_EXCEPTIONS_TABLE", "AWS_REGION": "ap-southeast-2", "STAGE": "dev"})
    mock_env.start()
    sm = boto3.client('secretsmanager', region_name='ap-southeast-2')
    sm.create_secret(
        Name="template-validator/dev/api-key", SecretString="{ \"api-key\": \"this is an api key! \" }"
    )

    response = app.lambda_handler(event, {}, dynamodb)

    mock_env.stop()

    return response


@mock_dynamodb2
class TestAccountHandling(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.tableName = "TEST_EXCEPTIONS_TABLE"
        cls.mock_ddb = mock_dynamodb2()
        cls.mock_ddb.start()
        cls.dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
        
        cls.mock_env = mock.patch.dict(os.environ, {"EXCEPTIONS_TABLENAME": cls.tableName, "AWS_REGION": "ap-southeast-2", "STAGE": "dev"})
        cls.mock_env.start()
        with open("tests/payloads/accounts_response.json") as file:
            cls.responseAccounts = file.read()

        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.mock_ddb.stop()
        cls.dynamodb = None
        cls.mock_env.stop()
        return super().tearDownClass()

    def setUp(self) -> None:
        self.table = helpers.createExceptionsTable(self.tableName, self.dynamodb)
        return super().setUp()

    def tearDown(self) -> None:
        self.table.delete()
        return super().tearDown()


    # When there is an access denied response from accounts api
    # then an HTTPError exception is thrown in populate_accounts_list()
    @mock_secretsmanager
    def test_accounts_no_auth(self) -> None:
        sm = boto3.client('secretsmanager', region_name='ap-southeast-2')
        sm.create_secret(
            Name="template-validator/dev", SecretString="{ \"api-key\": \"0123456789!\" }"
        ) 
        with requests_mock.Mocker() as mock_request:
            mock_request.get("https://ap-southeast-2-api.cloudconformity.com/v1/accounts", status_code=403)

            self.assertRaises(HTTPError, app.populate_accounts_list)


    # When the accounts API responds with valid data
    # and the account exists in that list
    # Then the correct CloudConformity ID is returned
    @mock_secretsmanager
    def test_get_valid_account(self) -> None:

        MOCK_VALID_AWS_ACCOUNT_ID = "010120201234"
        CC_ACCOUNT_ID = "Eas6c59rr"
        with requests_mock.Mocker() as mock_request:
            mock_request.get("https://ap-southeast-2-api.cloudconformity.com/v1/accounts", text=self.responseAccounts)

            app.populate_accounts_list()
            self.assertNotEqual(app.ACCOUNTS_LIST, [])

            print('ACCOUNTS_LIST:')
            for items in app.ACCOUNTS_LIST:
                print(items)

            actual_response = app.get_account(MOCK_VALID_AWS_ACCOUNT_ID)

            print(f'actual_response: {actual_response}')
            self.assertEqual(actual_response, CC_ACCOUNT_ID)

    # When the accounts API responds with valid data
    # and the account DOES NOT exist in that list
    # Then get_account() should return empty string
    def test_get_invalid_account(self) -> None:

        INVALID_ACCOUNT_ID = "0123456789012"

        with requests_mock.Mocker() as mock_request:
            mock_request.get("https://ap-southeast-2-api.cloudconformity.com/v1/accounts", text=self.responseAccounts)
 
            app.populate_accounts_list()
            self.assertNotEqual(app.ACCOUNTS_LIST, [])

            actual_response = app.get_account(INVALID_ACCOUNT_ID)

            self.assertEqual(actual_response, '')


    @mock_secretsmanager
    def test_api_key_headers(self) -> None:
        sm = boto3.client('secretsmanager', region_name='ap-southeast-2')
        sm.create_secret(
            Name="template-validator/dev", SecretString="{ \"api-key\": \"0123456789!\" }"
        )  
        app.populate_api_key()

        self.assertEqual(app.API_KEY, "0123456789!")



# load cc response into a string
# use in mock response
# get actual response from API g
# assert response = actual response.

# Add in timeout exception: exc=requests.exceptions.ConnectTimeout

@mock_dynamodb2
class TestLambdaFunctions(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.tableName = "TEST_EXCEPTIONS_TABLE"
        cls.mock_ddb = mock_dynamodb2()
        cls.mock_ddb.start()
        cls.dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
        
        cls.mock_env = mock.patch.dict(os.environ, {"EXCEPTIONS_TABLENAME": cls.tableName, "AWS_REGION": "ap-southeast-2", "STAGE": "dev"})
        cls.mock_env.start()
        with open("tests/payloads/templatescanner_response.json") as scannerAPIfile:
            cls.responseCCTemplateScannerAPI = scannerAPIfile.read()

        with open("tests/payloads/accounts_response.json") as accountsFile:
            cls.responseAccounts = accountsFile.read()

        with open("tests/payloads/s3_bucket_response.json") as s3ResponseFile:
            cls.validS3Response = s3ResponseFile.read()

        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.mock_ddb.stop()
        cls.dynamodb = None
        cls.mock_env.stop()
        return super().tearDownClass()

    def setUp(self) -> None:
        self.table = helpers.createExceptionsTable(self.tableName, self.dynamodb)
        return super().setUp()

    def tearDown(self) -> None:
        self.table.delete()
        return super().tearDown()

    def test_lambda_handler__valid_account(self):

        event = {
            "body": "{ \"accountId\" : \"012345678923\", \"templates\": [ {\r\n  \r\n  \"filename\" : \"mytemplate.yml\",\r\n  \"template\" : \"---\nAWSTemplateFormatVersion: '2010-09-09'\nResources:\n  S3Bucket:\n    Type: AWS::S3::Bucket\n    Properties:\n      AccessControl: PublicRead\"\r\n} ] }"
        }

        with requests_mock.Mocker() as mock_request:
            mock_request.get("https://ap-southeast-2-api.cloudconformity.com/v1/accounts", text=self.responseAccounts)
            mock_request.post("https://ap-southeast-2-api.cloudconformity.com/v1/template-scanner/scan", text=self.responseCCTemplateScannerAPI)
            actual_response = invoke_validate_handler(event, self.dynamodb)
        print("actual_response: " + json.dumps(actual_response, indent=2))

        results = json.loads(actual_response['body'])
        validResult = json.loads(self.validS3Response)
        self.assertDictEqual(results, validResult)

        assert actual_response["statusCode"] == 200

    def test_lambda_handler__invalid_account(self):

        event = {
            "body": "{ \"accountId\" : \"xyz\", \"templates\": [ {\r\n  \r\n  \"filename\" : \"mytemplate.yml\",\r\n  \"template\" : \"---\nAWSTemplateFormatVersion: '2010-09-09'\nResources:\n  S3Bucket:\n    Type: AWS::S3::Bucket\n    Properties:\n      AccessControl: PublicRead\"\r\n} ] }"
        }

        with requests_mock.Mocker() as mock_request:
            mock_request.get("https://ap-southeast-2-api.cloudconformity.com/v1/accounts", text=self.responseAccounts)
            mock_request.post("https://ap-southeast-2-api.cloudconformity.com/v1/template-scanner/scan", text=self.responseCCTemplateScannerAPI)
            actual_response = invoke_validate_handler(event, self.dynamodb)
     
        print("actual_response: " + json.dumps(actual_response, indent=2))
        response_body = json.loads(actual_response["body"], strict=False)
        self.assertEqual(actual_response['statusCode'], 200)

        # One extra failure, where account is invalid
        self.assertEqual(response_body["failures"]["VERY_HIGH"], 12)

    def test_lambda_handler__high_risk_template(self):

        event = {
            "body": "{ \"accountId\" : \"010120201234\", \"templates\": [ {\r\n  \r\n  \"filename\" : \"mytemplate.yml\",\r\n  \"template\" : \"---\nAWSTemplateFormatVersion: '2010-09-09'\nResources:\n  S3Bucket:\n    Type: AWS::S3::Bucket\n    Properties:\n      AccessControl: PublicRead\"\r\n} ] }"
        }

        with requests_mock.Mocker() as mock_request:
            mock_request.get("https://ap-southeast-2-api.cloudconformity.com/v1/accounts", text=self.responseAccounts)
            mock_request.post("https://ap-southeast-2-api.cloudconformity.com/v1/template-scanner/scan", text=self.responseCCTemplateScannerAPI)
            actual_response = invoke_validate_handler(event, self.dynamodb)
        print("actual_response: " + json.dumps(actual_response, indent=2))

        response_body = json.loads(actual_response["body"], strict=False)

        self.assertEqual(response_body["failures"]["VERY_HIGH"], 11)

    # # When there is no accountId field in the request
    # # Then there is a VERY_HIGH failure returned, in addition to usual template scans
    def test_no_account_data(self):

        event = {
            "body": "{\r\n  \"templates\" : [ { \"filename\" : \"mytemplate.yml\", \"template\": \"---\nAWSTemplateFormatVersion: '2010-09-09'\nResources:\n  S3Bucket:\n    Type: AWS::S3::Bucket\n    Properties:\n      AccessControl: PublicRead\"\r\n} ] }"
        }

        with requests_mock.Mocker() as mock_request:
            mock_request.get("https://ap-southeast-2-api.cloudconformity.com/v1/accounts", text=self.responseAccounts)
            mock_request.post("https://ap-southeast-2-api.cloudconformity.com/v1/template-scanner/scan", text=self.responseCCTemplateScannerAPI)
            actual_response = invoke_validate_handler(event, self.dynamodb)
        print("actual_response: " + json.dumps(actual_response, indent=2))

        self.assertEqual(actual_response['statusCode'], 200)

        response_body = json.loads(actual_response["body"], strict=False)

        self.assertEqual(response_body["failures"]["VERY_HIGH"], 12)

    # When there is no accountId field in the request
    # Then there is a VERY_HIGH failure returned, in addition to usual template scans
    def test_one_template(self):

        event = {
            "body": "{ \"accountId\" : \"010120201234\", \"templates\": [ {\r\n  \r\n  \"filename\" : \"mytemplate.yml\",\r\n  \"template\" : \"---\nAWSTemplateFormatVersion: '2010-09-09'\nResources:\n  S3Bucket:\n    Type: AWS::S3::Bucket\n    Properties:\n      AccessControl: PublicRead\"\r\n} ] }"
        }

        with requests_mock.Mocker() as mock_request:
            mock_request.get("https://ap-southeast-2-api.cloudconformity.com/v1/accounts", text=self.responseAccounts)
            mock_request.post("https://ap-southeast-2-api.cloudconformity.com/v1/template-scanner/scan", text=self.responseCCTemplateScannerAPI)
            actual_response = invoke_validate_handler(event, self.dynamodb)
        print("actual_response: " + json.dumps(actual_response, indent=2))

        self.assertEqual(actual_response['statusCode'], 200)

        response_body = json.loads(actual_response["body"], strict=False)

        self.assertEqual(response_body["failures"]["VERY_HIGH"], 11)
        self.assertEqual(response_body["failures"]["HIGH"], 2)
        self.assertEqual(response_body["failures"]["MEDIUM"], 2)
        self.assertEqual(response_body["failures"]["LOW"], 6)

    # When there is no accountId field in the request
    # Then there is a VERY_HIGH failure returned, in addition to usual template scans
    def test_two_templates(self):

        event = {
            "body": """{ \"accountId\" : \"010120201234\",
                       \"templates\": [ {\r\n  \r\n  \"filename\" : \"1.yml\",\r\n  \"template\" : \"---\nAWSTemplateFormatVersion: '2010-09-09'\nResources:\n  S3Bucket:\n    Type: AWS::S3::Bucket\n    Properties:\n      AccessControl: PublicRead\"\r\n},
                                        {\r\n  \r\n  \"filename\" : \"2.yml\",\r\n  \"template\" : \"---\nAWSTemplateFormatVersion: '2010-09-09'\nResources:\n  S3Bucket:\n    Type: AWS::S3::Bucket\n    Properties:\n      AccessControl: PublicRead\"\r\n} 
                                      ] }"""
        }

        with requests_mock.Mocker() as mock_request:
            mock_request.get("https://ap-southeast-2-api.cloudconformity.com/v1/accounts", text=self.responseAccounts)
            mock_request.post("https://ap-southeast-2-api.cloudconformity.com/v1/template-scanner/scan", text=self.responseCCTemplateScannerAPI)
            actual_response = invoke_validate_handler(event, self.dynamodb)
        print("actual_response: " + json.dumps(actual_response, indent=2))

        self.assertEqual(actual_response['statusCode'], 200)

        response_body = json.loads(actual_response["body"], strict=False)

        self.assertEqual(response_body["failures"]["VERY_HIGH"], 22)
        self.assertEqual(response_body["failures"]["HIGH"], 4)
        self.assertEqual(response_body["failures"]["MEDIUM"], 4)
        self.assertEqual(response_body["failures"]["LOW"], 12)

    def test_junk_payload(self):

        event = {
            "body": "{ \"this is not valid json\", \"tempbr\n  \"filename\" : \"mytemplate.yml\", }"
        }

        with requests_mock.Mocker() as mock_request:
            mock_request.get("https://ap-southeast-2-api.cloudconformity.com/v1/accounts", text=self.responseAccounts)
            mock_request.post("https://ap-southeast-2-api.cloudconformity.com/v1/template-scanner/scan", text=self.responseCCTemplateScannerAPI)
            actual_response = invoke_validate_handler(event, self.dynamodb)

        print("actual_response: " + json.dumps(actual_response, indent=2))

        self.assertEqual(actual_response['statusCode'], 500)
        self.assertEqual(actual_response['body'], '{"message": "Invalid JSON provided in request"}')

