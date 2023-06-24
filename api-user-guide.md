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

***

## getAllJobs
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

***

## getAllNonShortlistedResumes
This API gets all the resumes that are NOT shortlisted for a given Job ID.

### Access URL 
/api/v1/getAllNonShortlistedResumes

Method - POST

### Input Type

JSON 
### Input JSON Example

You need to call signIn API successfully. Access token received from successful signIN API should be passed as a bearer token in the header. 

{"jid":"1","criteria":""}

jid = Job ID for which you want to get the non shortlisted resumes

criteria = Free text search criteria used for filtering resumes to be returned. E.g. if you pass "Pune" in this , all resumes where location is matched to Pune is returned, if you pass "Pune and Java", all resumes where location is Pune and skills is Java is returned.

### Output Data Example

{
    "resumeList": [
        {
            "creation_date": "Fri, 07 Oct 2022 14:49:33 GMT",
            "email": "Testfornew@email.com",
            "id": 196,
            "is_deleted": false,
            "json_resume": null,
            "name": "Test for new",
            "notes": "Testing for new data",
            "phone": "989322128",
            "recently_added": false,
            "recruiter_id": 1,
            "resume_filename": null,
            "ts": null,
            "updation_date": null
        },
        {
            "creation_date": "Mon, 12 Sep 2022 17:21:54 GMT",
            "email": "kishan.gupta@gmail.com",
            "id": 148,
            "is_deleted": false,
            "json_resume": {
                "email": [
                    "kgupta9797@gmail.com"
                ],
                "name": [
                    "Kishan Gupta"
                ],
                "phone": [
                    "8421977236",
                    "+91-8421977236"
                ],
                "processed-date": "2022-09-12 17:21:54.805979+00:00",
                "raw-text": "Kishan Gupta\n\nJava Developer, Cognizant Technology Solutions, Pune\n\nEmail: kgupta9797@gmail.com\nMobile No: +91-8421977236\nGitHub : https://github.com/kgupta9797\nLinkedin: https://www.linkedin.com/in/kishan-gupta-614665177\nHackerrank: https://www.hackerrank.com/kishangupta097\n\nPersonal Summary\nJava Developer with 1.5 years  of professional hands-on experience in implementing Restful\nAPI,Enterprise Application development and writing test cases for delivery error less code. Good\nat coming up with optimized Problem Solving approaches.\n\nWork Experience\nMerck-SIP Integrations Project (Cognizant)\nAugust 2021 - Present\n\n● Handle multiple backend modules and ensure smooth functioning of the module.\n● Develop & manage APIs for various modules across products. Deploy & monitor\n\ncode throughout SDLC.\n\n● Implementing Data Migration between SIP module and SafeDX using Oracle 11G.\n● Implemented Multiple Complex Test scenario for testing existing legacy code.\n● Communicate and Coordinate with the development team and client for time eﬃciency.\n\ndelivery.\n\n.Additional Project\nPharmacy Medicine Supply Management System (Cognizant)\n-February  2021 - July 2021\n\n● Have  implemented a Java based Web Application using Spring, Spring Boot, Rest AP,I\n\nSpring Data JPA  And Microservices, Maven. ,\n\n● Implemented repository using H2 in memory Database.\n● Deployed this web application on Amazon EC2.\n● Tested the application using Junit Testing.\n\nTechnical Proﬁciency\n\n● Technologies: Java  8,OOPS, Spring Framework, Spring Boot, Spring Data JPA, Hibernate,,\n\n,Oracle SQL developer,Junit Testing,\n\n● Tools: Eclipse,Anypoint Studio,Postman,SVN,Maven, Spring Tool suite,\n\nEducation\nSinhgad College of Engineering,Pune\nBachelor of Engineering, Computer Engineering\nTTN Polytechnic,Akola\nPOST SSC Diploma, Maharashtra State Board\n\nCertiﬁcations/Courses\n\n● Core Java with Java 8 Features\n● Jr FSE development by CTS\n● Spring, Spring Boot Framework, Spring Data JPA,\n\n2017-2020\n(CGPA: 7.91)\n2013-2016\n(Percentage: 85.18%)\n\n\f",
                "top_skills": [
                    "1"
                ]
            }
        }
    ],
    "retCode": "JD_CRUD_S200",
    "retMsg": "Resumes not associated with job JD 1  fetched successfully.",
    "status": "Success"
}

### Output Data Notes

- retCode -> Always return type. JD_CRUD_S200 represents successful call
- retMsg -> Additional message. May be useful during error conditions
- Status ->"Success" if api call is success else "Fail"
- resumeList -> List of zero or more Resume records that are not associated for the given job id. Field level details to be added in case they are not self explanatory from the example given in the sample data.

***

## getAllShortlistedResumes
This API gets all the resumes that are already shortlisted for a given Job ID.

### Access URL 
/api/v1/getAllShortlistedResumes

Method - POST

### Input Type

JSON 
### Input JSON Example

You need to call signIn API successfully. Access token received from successful signIN API should be passed as a bearer token in the header. 

{"jid":"1"}

jid = Job ID for which you want to get the non shortlisted resumes


### Output Data Example

{
    "resumeList": [
        {
            "creation_date": "Fri, 07 Oct 2022 14:49:33 GMT",
            "email": "Testfornew@email.com",
            "id": 196,
            "is_deleted": false,
            "json_resume": null,
            "name": "Test for new",
            "notes": "Testing for new data",
            "phone": "989322128",
            "recently_added": false,
            "recruiter_id": 1,
            "resume_filename": null,
            "ts": null,
            "updation_date": null
        },
        {
            "creation_date": "Mon, 12 Sep 2022 17:21:54 GMT",
            "email": "kishan.gupta@gmail.com",
            "id": 148,
            "is_deleted": false,
            "json_resume": {
                "email": [
                    "kgupta9797@gmail.com"
                ],
                "name": [
                    "Kishan Gupta"
                ],
                "phone": [
                    "8421977236",
                    "+91-8421977236"
                ],
                "processed-date": "2022-09-12 17:21:54.805979+00:00",
                "raw-text": "Kishan Gupta\n\nJava Developer, Cognizant Technology Solutions, Pune\n\nEmail: kgupta9797@gmail.com\nMobile No: +91-8421977236\nGitHub : https://github.com/kgupta9797\nLinkedin: https://www.linkedin.com/in/kishan-gupta-614665177\nHackerrank: https://www.hackerrank.com/kishangupta097\n\nPersonal Summary\nJava Developer with 1.5 years  of professional hands-on experience in implementing Restful\nAPI,Enterprise Application development and writing test cases for delivery error less code. Good\nat coming up with optimized Problem Solving approaches.\n\nWork Experience\nMerck-SIP Integrations Project (Cognizant)\nAugust 2021 - Present\n\n● Handle multiple backend modules and ensure smooth functioning of the module.\n● Develop & manage APIs for various modules across products. Deploy & monitor\n\ncode throughout SDLC.\n\n● Implementing Data Migration between SIP module and SafeDX using Oracle 11G.\n● Implemented Multiple Complex Test scenario for testing existing legacy code.\n● Communicate and Coordinate with the development team and client for time eﬃciency.\n\ndelivery.\n\n.Additional Project\nPharmacy Medicine Supply Management System (Cognizant)\n-February  2021 - July 2021\n\n● Have  implemented a Java based Web Application using Spring, Spring Boot, Rest AP,I\n\nSpring Data JPA  And Microservices, Maven. ,\n\n● Implemented repository using H2 in memory Database.\n● Deployed this web application on Amazon EC2.\n● Tested the application using Junit Testing.\n\nTechnical Proﬁciency\n\n● Technologies: Java  8,OOPS, Spring Framework, Spring Boot, Spring Data JPA, Hibernate,,\n\n,Oracle SQL developer,Junit Testing,\n\n● Tools: Eclipse,Anypoint Studio,Postman,SVN,Maven, Spring Tool suite,\n\nEducation\nSinhgad College of Engineering,Pune\nBachelor of Engineering, Computer Engineering\nTTN Polytechnic,Akola\nPOST SSC Diploma, Maharashtra State Board\n\nCertiﬁcations/Courses\n\n● Core Java with Java 8 Features\n● Jr FSE development by CTS\n● Spring, Spring Boot Framework, Spring Data JPA,\n\n2017-2020\n(CGPA: 7.91)\n2013-2016\n(Percentage: 85.18%)\n\n\f",
                "top_skills": [
                    "1"
                ]
            }
        }
    ],
    "retCode": "JD_CRUD_S200",
    "retMsg": "Resumes not associated with job JD 1  fetched successfully.",
    "status": "Success"
}

### Output Data Notes

- retCode -> Always return type. JD_CRUD_S200 represents successful call
- retMsg -> Additional message. May be useful during error conditions
- Status ->"Success" if api call is success else "Fail"
- resumeList -> List of zero or more Resume records that are  associated for the given job id. Field level details to be added in case they are not self explanatory from the example given in the sample data.

***

