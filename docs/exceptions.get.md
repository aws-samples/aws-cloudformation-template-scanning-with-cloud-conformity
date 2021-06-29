# GET /exceptions

List all exception requests, and all approved exceptions

Note this does not interface with Cloud Conformity itself - the exceptions are stored in an internal database, not in Cloud Conformity itself. Having an appoved exception using this solution will not stop the check from failing if deployed into an AWS account scanned by Cloud Conformity.


**URL** : `/exceptions`

**Method** : `GET`

**Auth required** : NO (however it is private endpoint, API restricted to VPC with access to VPC endpoint


## Success Response

Returns a list of all exception requests, and all approved exceptions.

**Condition** : If all requests are accepted.

**Code** : `201 CREATED`

**Content example**

```json
{
  [
  {
    "awsAccountId": "111122223333",
    "filename": "packaged.yml",
    "ruleId": "ELBv2-004",
    "requestReason": "Only port 80 in ASG by design",
    "requestedBy": "Jane Roe",
    "approvedBy": "Sofía Martínez
  },
  ...
]
}
```

## Error Responses

**Condition** : If there is internal error listing exceptions.

**Code** : `500`

**Content** : 
```json
{ "message": "<failure reason>" }
````


