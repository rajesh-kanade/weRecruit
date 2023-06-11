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
    "status" : "Success" or "Fail"
}

### Output Data Notes

- retCode -> Always return type. IAM_CRUD_S200 represents successful login
- retMsg -> Additional message .
- roleID -> Represents the role ID of the successful logged in user.
- tenantID -> Represents the tenant ID of the successful logged in user.
- status -> Returns "Success" if api call is successful or "Fail" if api call has failed.

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
    "status" -> "Success"
}

### Output Data Notes

- retCode -> Always return type. RPT_CRUD_S200 represents successful call
- retMsg -> Additional message. May be useful during error conditions
- clientList -> List of zero or more client records. Each client record has following fields
    - client_id - Unique client ID 
    - client_name - Name of the client.
    - tenantID -> Tenant ID to which this client belongs.


## getAllClients
This API gets all the JDs for a tenant to which the logged in user belongs. 

### Access URL 
https://www.werecruit.cloud/api/v1/getAllJobs

Method - GET

### Input Type

JSON 
### Input JSON Example

You need to call signIn API successfully. Access token received from successful signIN API should be passed as a bearer token in the header. No other input parameters are required for this.

### Output Data Example
{
    "jdList": [
        {
            "city_id": 1,
            "client": "dec3-client-1",
            "client_id": 65,
            "ctc_currency": "INR",
            "ctc_max": "2000000.00",
            "ctc_min": "1500000.00",
            "details": null,
            "fees_in_percent": null,
            "hiring_mgr_emailid": "",
            "hiring_mgr_name": "",
            "hiring_mgr_phone": "",
            "hr_emailid": "",
            "hr_name": "",
            "hr_phone": "",
            "id": 101,
            "ip_emailid_1": "",
            "ip_emailid_2": "",
            "ip_name_1": "",
            "ip_name_2": "",
            "ip_phone_1": "",
            "ip_phone_2": "",
            "is_deleted": false,
            "jd_file_name": null,
            "jd_stats": null,
            "max_yrs_of_exp": "5.00",
            "min_yrs_of_exp": "2.00",
            "open_date": "Sat, 03 Dec 2022 05:41:03 GMT",
            "positions": 1,
            "primary_skills": "asfasfs",
            "recruiter_id": 1,
            "secondary_skills": "asfafsaf",
            "status": 0,
            "title": "Dec 3 client test",
            "top_skills": [],
            "warranty_period_in_months": null
        },
        {
            "city_id": 1,
            "client": "dec3-client-1",
            "client_id": 65,
            "ctc_currency": "USD",
            "ctc_max": "2000000.00",
            "ctc_min": "1000000.00",
            "details": null,
            "fees_in_percent": null,
            "hiring_mgr_emailid": "",
            "hiring_mgr_name": "",
            "hiring_mgr_phone": "",
            "hr_emailid": "",
            "hr_name": "",
            "hr_phone": "",
            "id": 100,
            "ip_emailid_1": "",
            "ip_emailid_2": "",
            "ip_name_1": "",
            "ip_name_2": "",
            "ip_phone_1": "",
            "ip_phone_2": "",
            "is_deleted": false,
            "jd_file_name": null,
            "jd_stats": null,
            "max_yrs_of_exp": "4.00",
            "min_yrs_of_exp": "2.00",
            "open_date": "Sat, 03 Dec 2022 05:39:59 GMT",
            "positions": 1,
            "primary_skills": "asdas",
            "recruiter_id": 1,
            "secondary_skills": "asfasfa",
            "status": 0,
            "title": "Test",
            "top_skills": [],
            "warranty_period_in_months": null
        }
    ]
    "retCode": "JD_CRUD_S200",
    "retMsg": "JD List successfully fetched from db for tenant ID",
    "status": "Success"
}
### Output Data Notes

- retCode -> Always return type. RPT_CRUD_S200 represents successful call
- retMsg -> Additional message. May be useful during error conditions
- Status ->"Success" if api call is success else "Fail"
- jdList -> List of zero or more JD records. Field level details to be added in case they are not self explanatory from the example given in the sample data.


