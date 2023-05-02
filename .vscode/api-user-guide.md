# weRecruit API Guide

## signIn API

### Access URL 
https://www.werecruit.cloud/api/v1/signIn

### Input Type
JSON 

### Input Data Example

{"Email":"replace with your EmailAddress>","password":"replace with your password"}

### Output Type
JSON

### Output Data Example

{
    "access_token": "sample",
    "retCode": "IAM_CRUD_S200",
    "retMsg": "User List successfully fetched from db",
    "roleID": 1,
    "tenantID": 5
}

### Output Data Notes

- retCode -> Always return type. IAM_CRUD_S200 represents successful login
- retMsg -> Additional message .
- roleID -> Represents the role ID of the successful logged in user.
- tenantID -> Represents the tenant ID of the successful logged in user.



