# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
sampleInput = """{
  "data": [
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-001:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "FAILURE",
        "risk-level": "VERY_HIGH",
        "pretty-risk-level": "Very High",
        "message": "Bucket S3Bucket allows public 'READ' access.",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket Public 'READ' Access",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-001"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-002:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "SUCCESS",
        "risk-level": "VERY_HIGH",
        "pretty-risk-level": "Very High",
        "message": "Bucket S3Bucket does not allow public 'READ_ACP' access",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket Public 'READ_ACP' Access",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-002"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-003:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "SUCCESS",
        "risk-level": "VERY_HIGH",
        "pretty-risk-level": "Very High",
        "message": "Bucket S3Bucket does not allow public 'WRITE' access",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket Public 'WRITE' Access",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-003"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-004:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "SUCCESS",
        "risk-level": "VERY_HIGH",
        "pretty-risk-level": "Very High",
        "message": "Bucket S3Bucket does not allow public 'WRITE ACP' access",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket Public 'WRITE_ACP' Access",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-004"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-005:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "SUCCESS",
        "risk-level": "VERY_HIGH",
        "pretty-risk-level": "Very High",
        "message": "Bucket S3Bucket does not allow public 'FULL_CONTROL' access",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket Public 'FULL_CONTROL' Access",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-005"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-006:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "SUCCESS",
        "risk-level": "VERY_HIGH",
        "pretty-risk-level": "Very High",
        "message": "Bucket S3Bucket does not allow authenticated users 'READ' access",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket Authenticated Users 'READ' Access",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-006"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-007:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "SUCCESS",
        "risk-level": "VERY_HIGH",
        "pretty-risk-level": "Very High",
        "message": "Bucket S3Bucket does not allow authenticated users 'READ_ACP' access",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket Authenticated Users 'READ_ACP' Access",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-007"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-008:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "SUCCESS",
        "risk-level": "VERY_HIGH",
        "pretty-risk-level": "Very High",
        "message": "Bucket S3Bucket does not allow authenticated users 'WRITE' access",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket Authenticated Users 'WRITE' Access",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-008"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-009:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "SUCCESS",
        "risk-level": "VERY_HIGH",
        "pretty-risk-level": "Very High",
        "message": "Bucket S3Bucket does not allow authenticated users 'WRITE_ACP' access",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket Authenticated Users 'WRITE_ACP' Access",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-009"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-010:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "SUCCESS",
        "risk-level": "VERY_HIGH",
        "pretty-risk-level": "Very High",
        "message": "Bucket S3Bucket does not allow authenticated users 'FULL_CONTROL' access",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket Authenticated Users 'FULL_CONTROL' Access",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-010"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-011:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "FAILURE",
        "risk-level": "MEDIUM",
        "pretty-risk-level": "Medium",
        "message": "Bucket S3Bucket doesn't have access logging enabled",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket Logging Enabled",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-011"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-012:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "FAILURE",
        "risk-level": "LOW",
        "pretty-risk-level": "Low",
        "message": "Bucket S3Bucket does not have versioning enabled",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "reliability"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket Versioning Enabled",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-012"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-013:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "FAILURE",
        "risk-level": "LOW",
        "pretty-risk-level": "Low",
        "message": "Bucket S3Bucket configuration is MFA-Delete disabled",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket MFA Delete Enabled",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-013"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-018:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "SUCCESS",
        "risk-level": "LOW",
        "pretty-risk-level": "Low",
        "message": "Bucket S3Bucket is using a DNS-compliant name",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "performance-efficiency"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "DNS Compliant S3 Bucket Names",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-018"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-020:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "FAILURE",
        "risk-level": "LOW",
        "pretty-risk-level": "Low",
        "message": "Bucket S3Bucket does not utilize lifecycle configurations",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security",
          "cost-optimisation"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Buckets Lifecycle Configuration",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-020"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-021:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "FAILURE",
        "risk-level": "HIGH",
        "pretty-risk-level": "High",
        "message": "Bucket S3Bucket doesn't have encryption enabled",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Bucket Default Encryption",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-021"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-023:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "FAILURE",
        "risk-level": "LOW",
        "pretty-risk-level": "Low",
        "message": "Object Lock is not enabled for S3Bucket",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Object Lock",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-023"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-024:S3:us-east-1:S3Bucket",
      "attributes": {
        "region": "us-east-1",
        "status": "FAILURE",
        "risk-level": "LOW",
        "pretty-risk-level": "Low",
        "message": "Transfer Acceleration is not enabled for S3Bucket",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "performance-efficiency"
        ],
        "last-updated-date": null,
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "S3 Transfer Acceleration",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-024"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    },
    {
      "type": "checks",
      "id": "ccc:AccountId:S3-026:S3:global:S3Bucket",
      "attributes": {
        "region": "global",
        "status": "FAILURE",
        "risk-level": "VERY_HIGH",
        "pretty-risk-level": "Very High",
        "message": "s3-bucket S3Bucket does not have S3 Block Public Access feature enabled.",
        "resource": "S3Bucket",
        "descriptorType": "s3-bucket",
        "categories": [
          "security"
        ],
        "last-updated-date": null,
        "extradata": [],
        "tags": [],
        "cost": 0,
        "waste": 0,
        "not-scored": false,
        "ignored": false,
        "rule-title": "Enable S3 Block Public Access for S3 Buckets",
        "provider": "aws"
      },
      "relationships": {
        "rule": {
          "data": {
            "type": "rules",
            "id": "S3-026"
          }
        },
        "account": {
          "data": {
            "type": "accounts",
            "id": "AccountId"
          }
        }
      }
    }
  ],
  "meta": {
    "missingParameters": [],
    "errors": []
  }
}"""

# sampleOutput = """