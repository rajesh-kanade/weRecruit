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
from dataclasses import dataclass

import os
from enum import Enum

class Status(Enum):
    active = 0
    deleted = -1

@dataclass(frozen=True)
class User:
	id: str
	name: str
	password: str
	status : int =  Status.active.value

def create_user(user_attrs):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = db_con.cursor()

		if user_attrs is None or len(user_attrs) <= 0 :
			 return(1,"user attributes dictionary is either None or empty.", None)
		
		if 'id' not in user_attrs.keys():
			 return(2,"User Id not found.", None)
		
		if 'name' not in user_attrs.keys():
			 return(3,"User name not found.", None)

		if 'status' not in user_attrs.keys():
			 return(4,"User status not found.", None)

		if 'password' not in user_attrs.keys():
			 return(5,"User password not found.", None)

		userID = user_attrs['id'].strip()
		name = user_attrs['name'].strip()
		status = user_attrs['status']
		password = user_attrs['password'].strip()

		if not userID:
			 return(21,"User Id empty.", None)

		if not name:
			 return(22,"Name empty.", None)

		if not password:
			 return(22,"password empty.", None)

		#TODO check status value is as defined in enum
		
		#TODO hash the password

		sql = """insert into fl_iam_users ( id, name, status, password) 
				values (%s,%s, %s,%s)"""
		params = (userID,name,status,password)
		print ( cursor.mogrify(sql, params))
		
		cursor.execute(sql, params)
		effected_rows = cursor.rowcount			
		if effected_rows == 1:
			db_con.commit()
			return (0, "User insertion successed.", effected_rows)
		else:
			db_con.rollback()
			return (50, "User insertion effected more then 1 rows.", effected_rows)

	except Exception as e:
		print(e)
		db_con.rollback()
		return (-1, str(e),None)
	
	finally:
		if cursor is not None:
			cursor.close()
		dbUtils.returnToPool(db_con)


def update_user(userID,update_attrs):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = db_con.cursor()

		if update_attrs is None or len(update_attrs) <= 0 :
			 return(1,"update attributes dictionary is either None or empty.", None)
		#TODO: Check column key is valid key representing a column

		if len(update_attrs) ==1:
			sql = "UPDATE fl_iam_users SET {} = %s WHERE id = %s"	
			sql = sql.format(list(update_attrs.keys())[0])
			params = (list(update_attrs.values())[0],userID)
		else:
			sql = "UPDATE fl_iam_users SET ({}) = %s WHERE id = '{}'"
			sql = sql.format(', '.join(update_attrs.keys()), str(userID))
			params = (tuple(update_attrs.values()),)

		print ( cursor.mogrify(sql, params))
		
		cursor.execute(sql, params)
		updated_rows = cursor.rowcount
			
		if updated_rows == 1:
			db_con.commit()
			return (0, "User update successed.", updated_rows)
		else:
			db_con.rollback()
			return (2, "User update failed.", updated_rows)

	except Exception as e:
		print(e)
		db_con.rollback()
		return (-1, str(e),None)
	
	finally:
		if cursor is not None:
			 cursor.close()
		dbUtils.returnToPool(db_con)



def delete_user(userID):
	try:
		
		db_con = dbUtils.getConnFromPool()		
		cursor = dbUtils.getNamedTupleCursor(db_con)

		sql = """UPDATE fl_iam_users SET status = %s WHERE id = %s"""		
		params = (Status.deleted.value,userID)
		
		print (sql)		
		print ( cursor.mogrify(sql, params))

		cursor.execute(sql, params)
		updated_rows = cursor.rowcount

		db_con.commit()
		
		if updated_rows != 1 :
			return(1, "DELETE for User ID '{0}' failed.".format(userID), updated_rows)
		else:
			return(0, "DELETE for User ID '{0}' succeeded.".format(userID),None)
	
	except Exception as e:
		print(e)
		return(-1, str(e), None) 

	finally:
		if cursor is not None : 
			cursor.close()

		dbUtils.returnToPool(db_con)

def get_user(userID):
	
	try:
		
		db_con = dbUtils.getConnFromPool()		
		cursor = dbUtils.getNamedTupleCursor(db_con)

		sql = """SELECT id,name FROM fl_iam_users WHERE id = %s and status = %s """		
		params = (userID,Status.active.value)
		
		print (sql)		
		print ( cursor.mogrify(sql, params))

		cursor.execute(sql, params)

		userList =cursor.fetchall()

		if userList == None or len(userList) <= 0 :
			return(1, "User ID '{0}' not found in database".format(userID), None)

		if userList == None or len(userList) > 1 :
			return(2, "'{0}' records found for User ID '{1}'".format(len(userList),userID), len(userList))

		for user in userList:
			print(user)

		return(0, "User ID '{0}' successfully fetched from db".format(userID), userList[0])
	
	except Exception as e:
		print(e)
		return(-1, str(e), None) 

	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)


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
	
	#(retCode, msg ) = signUp("Rajesh Kanade", "rrkanade@yahoo.com")
	#(retCode, msg, userRecord ) = get_user("rajesh")
	#(retCode, msg, userRecord ) = delete_user("rajesh")
	
	"""
	(retCode, msg, userRecord ) = update_user("rajesh",{'status':Status.active.value,'name':'rajesh python'})
	
	(retCode, msg, userRecord ) = update_user("rajesh",{})
	(retCode, msg, userRecord ) = update_user("rajesh",{'name':'vs code'})
	
	print( retCode)
	print ( msg)
	print ( userRecord)
	
	"""
	(retCode, msg, userRecord ) = create_user({'id':'rk1','name':'R K 3','status':0,'password':'pwd'})
	#(retCode, msg, userRecord ) = create_user({'id':'RK2','status':Status.active.value,'name':'R K 2','password':'dummy'})

	print( retCode)
	print ( msg)
	print ( userRecord)
