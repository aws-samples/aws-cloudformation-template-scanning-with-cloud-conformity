# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json
import os
import requests_mock
import boto3
from moto import mock_dynamodb2, mock_secretsmanager
from unittest import mock
from unittest import TestCase

from validate import app, exceptions
import tests.unit.helpers as helpers

@mock_secretsmanager
def invoke_validate_handler(event):
    mock_env = mock.patch.dict(os.environ, {"AWS_REGION": "ap-southeast-2", "STAGE": "dev"})
    mock_env.start()
    sm = boto3.client('secretsmanager', region_name='ap-southeast-2')
    sm.create_secret(
        Name="template-validator/dev", SecretString="{ \"api-key\": \"this is an api key! \" }"
    )

    response = app.lambda_handler(event, {})

    mock_env.stop()

    return response

@mock_dynamodb2
class TestExceptions(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print('SETTING UP!')
        cls.tableName = "TEST_EXCEPTIONS_TABLE"
        cls.mock_env = mock.patch.dict(os.environ, {"EXCEPTIONS_TABLENAME": cls.tableName, "AWS_REGION": "ap-southeast-2", "STAGE": "dev"})
        cls.mock_env.start()

        with open("tests/payloads/templatescanner_response.json") as scannerAPIfile:
            cls.responseCCTemplateScannerAPI = scannerAPIfile.read()

        with open("tests/payloads/accounts_response.json") as accountsFile:
            cls.responseAccounts = accountsFile.read()

        with open("tests/payloads/s3_bucket_response.json") as s3ResponseFile:
            cls.validS3Response = s3ResponseFile.read()

        cls.mock_ddb = mock_dynamodb2()
        cls.mock_ddb.start()
        cls.dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        print('TEARING DOWN!')
        cls.mock_ddb.stop()
        cls.dynamodb = None
        cls.mock_env.stop()
        return super().tearDownClass()

    def setUp(self) -> None:
        print("setUp()")
        self.table = helpers.createExceptionsTable(self.tableName, self.dynamodb)
        return super().setUp()

    def tearDown(self) -> None:
        print("tearDown()")
        self.table.delete()
        return super().tearDown()

    def test_missing_elements(self):

        # 1. Add exception for check in 1.yml
        ruleException = """[{"awsAccountId": "010120201234",
                          "filename": "1.yml"""

        addEvent = {"body": ruleException}
        addResponse = exceptions.request(addEvent, {}, self.dynamodb)

        print("actual_response: " + json.dumps(addResponse, indent=2))

        self.assertEqual(addResponse['statusCode'], 500)

    def test_approve_invalid(self):

        # There is nothing in db yet, so approval should fail
        approval = """{"awsAccountId": "010120201234",
                          "filename": "1.yml",
                          "ruleId": "S3-013",
                          "approvedBy": "H Simpson"}"""

        approvalEvent = {"body": approval}
        approvalResponse = exceptions.approve(approvalEvent, {}, self.dynamodb)

        self.assertEqual(approvalResponse['statusCode'], 500)

    def test_approval_process(self):

        # 1. Add exception for check in 1.yml
        ruleException = """[{"awsAccountId": "010120201234",
                          "filename": "1.yml",
                          "ruleId": "S3-013",
                          "requestReason": "Cyber is ok with this bucket not having MFA delete enabled",
                          "requestedBy": "J Doe"}]"""

        addEvent = {"body": ruleException}
        addResponse = exceptions.request(addEvent, {}, self.dynamodb)

        print("actual_response: " + json.dumps(addResponse, indent=2))

        self.assertEqual(addResponse['statusCode'], 201)

        response_body = self.execute_validation_api()

        # Should be 12, not 11 - as no rule has been exempted
        self.assertEqual(response_body["failures"]["LOW"], 12)
        self.assertNotIn("EXEMPTED", response_body["failures"])

        # Now approve the request
        approval = """{"awsAccountId": "010120201234",
                          "filename": "1.yml",
                          "ruleId": "S3-013",
                          "approvedBy": "H Simpson"}"""

        approvalEvent = {"body": approval}
        approvalResponse = exceptions.approve(approvalEvent, {}, self.dynamodb)

        self.assertEqual(approvalResponse['statusCode'], 201)

    def test_get_approved_exceptions(self):
        # 1. Add exception for check in 1.yml
        ruleException = """[{"awsAccountId": "010120201234",
                          "filename": "1.yml",
                          "ruleId": "S3-013",
                          "requestReason": "Cyber is ok with this bucket not having MFA delete enabled",
                          "requestedBy": "J Doe"}]"""

        addEvent = {"body": ruleException}
        addResponse = exceptions.request(addEvent, {}, self.dynamodb)
        self.assertEqual(addResponse['statusCode'], 201)

        # 2. Check dict from get_appproved_exceptions - should be empty as not approved
        exceptionsDict = exceptions.get_approved_exceptions("010120201234", self.dynamodb)
        self.assertEqual(len(exceptionsDict), 0)

        # 3. Now approve the request
        approval = """{"awsAccountId": "010120201234",
                          "filename": "1.yml",
                          "ruleId": "S3-013",
                          "approvedBy": "H Simpson"}"""

        approvalEvent = {"body": approval}
        approvalResponse = exceptions.approve(approvalEvent, {}, self.dynamodb)

        self.assertEqual(approvalResponse['statusCode'], 201)

        # 4. Now check dict
        exceptionsDict = exceptions.get_approved_exceptions("010120201234", self.dynamodb)
        self.assertEqual(len(exceptionsDict), 1)
        self.assertIn("1.yml#S3-013", exceptionsDict)
        self.assertIn("approved", exceptionsDict["1.yml#S3-013"])
        self.assertEqual(exceptionsDict["1.yml#S3-013"]["approvedBy"], "H Simpson")


    def test_remove_exceptions(self):
        # 1. Add exception for check in 1.yml
        ruleException = """[{"awsAccountId": "010120201234",
                          "filename": "1.yml",
                          "ruleId": "S3-013",
                          "requestReason": "Cyber is ok with this bucket not having MFA delete enabled",
                          "requestedBy": "J Doe"}]"""

        addEvent = {"body": ruleException}
        addResponse = exceptions.request(addEvent, {}, self.dynamodb)
        self.assertEqual(addResponse['statusCode'], 201)

        # 2. Now approve the request
        approval = """{"awsAccountId": "010120201234",
                          "filename": "1.yml",
                          "ruleId": "S3-013",
                          "approvedBy": "H Simpson"}"""

        approvalEvent = {"body": approval}
        approvalResponse = exceptions.approve(approvalEvent, {}, self.dynamodb)

        self.assertEqual(approvalResponse['statusCode'], 201)

        # 4. Now check dict
        exceptionsDict = exceptions.get_approved_exceptions("010120201234", self.dynamodb)
        self.assertEqual(len(exceptionsDict), 1)
        self.assertIn("1.yml#S3-013", exceptionsDict)
        self.assertIn("approved", exceptionsDict["1.yml#S3-013"])
        self.assertEqual(exceptionsDict["1.yml#S3-013"]["approvedBy"], "H Simpson")

        # 5. Now remove the exception
        removalBody = """{"awsAccountId": "010120201234",
                    "filename": "1.yml",
                    "ruleId": "S3-013",
                    "approvedBy": "H Simpson"}"""
        

        removeEvent = {"body": removalBody}
        removeResponse = exceptions.delete(removeEvent, {}, self.dynamodb)
        self.assertEqual(removeResponse['statusCode'], 200)

        # check nothing in the dict anymore
        exceptionsDict = exceptions.get_approved_exceptions("010120201234", self.dynamodb)
        self.assertEqual(len(exceptionsDict), 0)

    def execute_validation_api(self):
        # 2. Now run scripts through validate api
        event = {
            "body": """{ \"accountId\" : \"010120201234\",
                       \"templates\": [ {\r\n  \r\n  \"filename\" : \"1.yml\",\r\n  \"template\" : \"---\nAWSTemplateFormatVersion: '2010-09-09'\nResources:\n  S3Bucket:\n    Type: AWS::S3::Bucket\n    Properties:\n      AccessControl: PublicRead\"\r\n},
                                        {\r\n  \r\n  \"filename\" : \"2.yml\",\r\n  \"template\" : \"---\nAWSTemplateFormatVersion: '2010-09-09'\nResources:\n  S3Bucket:\n    Type: AWS::S3::Bucket\n    Properties:\n      AccessControl: PublicRead\"\r\n} 
                                      ] }"""
        }

        with requests_mock.Mocker() as mock_request:
            mock_request.get("https://ap-southeast-2-api.cloudconformity.com/v1/accounts", text=self.responseAccounts)
            mock_request.post("https://ap-southeast-2-api.cloudconformity.com/v1/template-scanner/scan", text=self.responseCCTemplateScannerAPI)
            actual_response = invoke_validate_handler(event)
        print("actual_response: " + json.dumps(actual_response, indent=2))

        self.assertEqual(actual_response['statusCode'], 200)

        response_body = json.loads(actual_response["body"], strict=False)

        return response_body
