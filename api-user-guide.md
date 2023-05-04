# weRecruit API Guide

## signIn
signIn API is one of the first API typically a developer would like to invoke and get access to the token. Most of the other API are behind auth wall and will need the bearer token to be passed in the header.
### Access URL 
https://www.werecruit.cloud/api/v1/signIn
Method - POST

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

***
## getAllClients
This API gets all the clients for a tenant to which the logged in user belongs. 

### Access URL 
https://www.werecruit.cloud/api/v1/getAllClients

Method - GET

### Input Type

JSON 
### Input JSON Example

You need to call signIn API successfully. Access token received from successful signIN API should be passed as a bearer token in the header. No other input parameters are required for this.

### Output Data Example

{
    "clientList": [
        {
            "client_id": 3,
            "client_name": "1213",
            "tenant_id": 1
        },
        {
            "client_id": 4,
            "client_name": "22June",
            "tenant_id": 1
        },
        {
            "client_id": 60,
            "client_name": "WIPRO",
            "tenant_id": 1
        }
    ],
    "retCode": "RPT_CRUD_S200",
    "retMsg": "Client List fetched successfully from db for tenant ID 1"
}

### Output Data Notes

- retCode -> Always return type. RPT_CRUD_S200 represents successful call
- retMsg -> Additional message. May be useful during error conditions
- clientList -> List of zero or more client records. Each client record has following fields
    - client_id - Unique client ID 
    - client_name - Name of the client.
    - tenantID -> Tenant ID to which this client belongs.
