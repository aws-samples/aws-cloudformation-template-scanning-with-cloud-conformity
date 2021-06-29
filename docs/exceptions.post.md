# POST /exceptions

Request a failing check to be exempted from any future template scan results

**URL** : `/exceptions`

**Method** : `POST`

**Auth required** : NO (however it is private endpoint, API restricted to VPC with access to VPC endpoint

**Data example** All fields must be sent.


```json
[
  {
    "awsAccountId": "111122223333",
    "filename": "packaged.yml",
    "ruleId": "ELBv2-004",
    "requestReason": "Only port 80 in ASG by design",
    "requestedBy": "Jane Roe"
  },
  ...
]
```

Exceptions use the key of `awsAccountId` + `filename` + `ruleId` to uniquely identify the exception request.


## Success Response

**Condition** : If all requests are accepted.

**Code** : `201 CREATED`

**Content example**

```json
{}
```

## Error Responses

**Condition** : If there is internal error adding exceptions.

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

