# POST /validate

Send the provided AWS CloudFormation templates using the Conformity Template Scanner API.

Returns the results in Cucumber JSON format, readable by AWS CodeBuild reports

**URL** : `/validate`

**Method** : `POST`

**Auth required** : NO

**Permissions required** : Private endpoint, API restricted to VPC with access to VPC endpoint

**Data example** All fields must be sent.

```json
{
  "accountId" : "<AWS account id from caller>",
  "templates" : [  
    {
      "filename" : "mytemplate.yml",
      "template": "<stringified cloudformation template>"
    },
    {
      "filename" : "mytemplate.json",
      "template": "<stringified cloudformation template>"
    }
  ]
}
```

## Success Response

**Condition** : If all templates scanned successfully by Conformity.

**Code** : `201 CREATED`

**Content example**

```json
{
  "failures": {
    "VERY_HIGH": 12,
    "HIGH": 2,
    "MEDIUM": 2,
    "LOW": 6
  },
  "results" : "<cucumber JSON with validate results>"
}
```

## Error Responses

**Condition** : If CloudConformity returns error scanning the templates.

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

