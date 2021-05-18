#import sqlite3
import constants
import datetime
#import pandas as pd
#from pandas.io.json import json_normalize
import json
from jinja2 import Environment, FileSystemLoader
import emailUtils
import psycopg2
import dbUtils

from datetime import date

from flask import Flask, jsonify, request 

import random
from flask_mail import Mail, Message 
from flask_cors import CORS

from werkzeug.utils import secure_filename

import os

def checkUserExist(email):
    try:
        return True
    except Exception as e:
        return False

def getUsersForApp (appcode):

    userList =[] #empty userList 

    try:
        #db_con = sqlite3.connect(constants.DB_NAME)
        db_con = dbUtils.getConnFromPool()
        cursor = db_con.cursor()
        
        query = """SELECT "user-id" FROM "user-app" WHERE "app-id" = %s """
        data_tuple = (appcode,)
        print (query)
        
        cursor.execute(query, data_tuple)
        records = cursor.fetchall()
        print("Total rows are:  ", len(records))
        print("Printing each row")

        for row in records:
            print("User ID is : ", row[0])
            userList.append( str(row[0]))

    except Exception as e:
        print(e)
        return(-1, str(e), None)

    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)

    return (0, "successful", userList )

def getUserConfig(userID, appcode,key):
    try:
        #db_con = sqlite3.connect(constants.DB_NAME)
        db_con = dbUtils.getConnFromPool()
        cursor = db_con.cursor()
        
        query = """SELECT config -> %s as value FROM "user-app-config" WHERE user_id = %s and app_id = %s and config ?  %s """
        data_tuple = (str(key), str(userID), str(appcode), str(key))
        print (query)
        print ( data_tuple)
        cursor.execute(query, data_tuple)
        records = cursor.fetchall()
        print("Total rows are:  ", len(records))
        
        if (len(records) ==1):
            row = records[0]
            print("Config Value is : ", row[0])
            return (0, 'success', row[0])
        else:
            if (len(records) == 0):
                return (1,'Config key not found.', None)
            if ( len(records) > 1):
                return (2,'Too many values for the specified Config key.', None)

    except Exception as e:
        print(e)
        return ( -1, print(e), None)
        
    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)


def signUp(username, email,status=1):

    error = ''
    try:

        try:
            #db_con = sqlite3.connect(constants.DB_NAME)
            #db_con = psycopg2.connect(host="localhost",database="recruitment-hub", user="postgres",password="rajaram1909")
            db_con = dbUtils.getConnFromPool()
            cursor = db_con.cursor()

            #insert into user table
            insert_query = """INSERT INTO public.user (id, name,email,status) VALUES (%s,%s,%s,%s)"""
            
            data_tuple = (email, username, email,status)
            cursor.execute(insert_query, data_tuple)
            
            db_con.commit()
            return (0, "User signed up successfully.")

        except Exception as dbe:
            print(dbe)
            db_con.rollback()
            return (-1, str(dbe))
    
        finally:
            cursor.close()
            dbUtils.returnToPool(db_con)

        #return jsonify({'retcode': 0},{'msg': 'User created successfully.'})

    except Exception as e:
        #flash(e)
        print ("In the exception block.")
        return ( -2, str(e))
        #return jsonify({'retcode': -101},{'msg': str(e)}) 

def userSignIn(email, otp):
    error = ''
    try:

        try:
            db_con = dbUtils.getConnFromPool()
            cursor = db_con.cursor()

            #insert into user table
            query = """SELECT COUNT(*) FROM public.user WHERE
                    id = %s and otp = %s """
        
            data_tuple = (email, otp)

            print (query)
            cursor.execute(query, data_tuple)
            (number_of_rows,)=cursor.fetchone()
            print ( "No of rows returned : " +str(number_of_rows))

            if (number_of_rows) == 1 :
                return (0, "Login successful.")
                #return jsonify({'retcode': 0},{'msg': 'login Successful'})
            else:
                return ( -1, "Login failed as no user found.")
                #return jsonify({'retcode': -1},{'msg': 'login failed'})
                

        except Exception as dbe:
            print(dbe)
            return ( -2, str(dbe))
            #db_con.rollback()
            #raise
        
        finally:
            cursor.close()
            dbUtils.returnToPool(db_con)	

    except Exception as e:
        #flash(e)
        print ("In the exception block.")
        print(e)
        return ( -2, str(e))
        #return jsonify({'retcode': -101},{'msg': str(e)}) 


def getOTP(email):
    try:

        # All validations passed now generate OTP and send email
        otp = random.randint(1000,9999)

        #update the user table 
        try:
            #db_con = sqlite3.connect(constants.DB_NAME)
            db_con = dbUtils.getConnFromPool()

            cursor = db_con.cursor()

            #insert into user table
            query = """UPDATE public.user SET otp = %s WHERE email = %s"""
            print(query)

            data_tuple = (str(otp), email)

            cursor.execute(query, data_tuple)

            #(number_of_rows,)=cursor.fetchone()
            if (cursor.rowcount) != 1 :
                db-con.rollback()
                return (-1, "Failed to update OTP.")
                #return jsonify({'retcode': -104},{'msg': 'Failed to update OTP'})

            db_con.commit()
            
        except Exception as dbe:
            print(dbe)
            db_con.rollback()
            return (-1, str(e))

            #return -1
            #raise
        finally:
            cursor.close()
            dbUtils.returnToPool(db_con)

        file_loader = FileSystemLoader('./conf')
        env = Environment(loader=file_loader)
        template = env.get_template('OTPEmail.template')
        
        body = template.render(otp = str(otp),expiryMinutes = "5" )

        #send email 
        emailUtils.sendMail(email,'Fulgorithm OTP Confirmation' , body,'plain' )

        print("Email sent successfully.")
        return (0, "OT successesfully sent to registered email ID.")
        #return jsonify({'retcode': 0},{'msg':'OTP successfully sent to registered email ID.'})	

    except Exception as e:
        print ("In the exception block.")
        print(e)
        return (-2, str(e))
        #return jsonify({'retcode': -110},{'msg':str(e)}) 


## main entry point
if __name__ == "__main__":
    #getUserConfigList('rrkanade22@yahoo.com','CAMI')
    #value = getUserConfig('rrkanade22@yahoo.com','CAMI', "email_server")
    #print(value)
    #getUsersForApp(constants.APP_CODE_CAMI)
    #getSummaryReportForToday( 'rrkanade22@yahoo.com' )
    
    (retCode, msg ) = signUp("Rajesh Kanade", "rrkanade@yahoo.com")
    print( retCode)
    print ( msg)
    