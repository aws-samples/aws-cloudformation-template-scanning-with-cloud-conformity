# DELETE /exceptions

Delete an existing exception request or approved request

Note this does not interface with Cloud Conformity itself - the exception request is stored in an internal database, not in Cloud Conformity itself. Having an appoved exception using this solution will not stop the check from failing if deployed into an AWS account scanned by Cloud Conformity.


**URL** : `/exceptions`

**Method** : `DELETE`

**Auth required** : NO (however it is private endpoint, API restricted to VPC with access to VPC endpoint

**Data example** All fields must be sent.


```json
[
  {
    "awsAccountId": "111122223333",
    "filename": "packaged.yml",
    "ruleId": "ELBv2-004",
    "approvedBy": "Sofía Martínez"
  },
  ...
]
```

Exceptions use the key of `awsAccountId` + `filename` + `ruleId` to uniquely identify the exception request.

## Success Response

**Condition** : If the request is successfully deleted.

**Code** : `200 SUCCESS`

**Content example**

```json
{}
```

## Error Responses

**Condition** : If there is internal error approving the exception request

**Code** : `500`

**Content** : 
```json
{ "message": "<failure reason>" }
````

### Or

**Condition** : If fields are missing or malformed in request body.

**Code** : `400 BAD REQUEST`

**Content example**

**Content** : 
```json
{ "message": "<failure reason>" }
````

