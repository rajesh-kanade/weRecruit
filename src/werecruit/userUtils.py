#import fulgorithm.constants
import datetime

import json
from jinja2 import Environment, FileSystemLoader
#import emailUtils
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

import hashlib

class Status(Enum):
	active = 1
	suspended = 0
	pending_verification = 2

class RetCodes(Enum):
	success = 'IAM_CRUD_S200'
	missing_ent_attrs_error = "IAM_CRUD_E400"
	empty_ent_attrs_error = "IAM_CRUD_E401"
	save_ent_error = "IAM_CRUD_E403"
	del_ent_error = "IAM_CRUD_E404"
	get_ent_error = "IAM_CRUD_E405"
	server_error = "IAM_CRUD_E500"
	sign_in_failed = "IAM_CRUD_E411"

'''@dataclass(frozen=True)
class User:
	id: str
	name: str
	email : str
	password: str
	status : int =  Status.active.value
	is_deleted : bool = False
'''
'''
@dataclass(frozen=True)
class Tenant:
	id: int
	name:str
	admin_id : str
	status : int =  Status.active.value
	is_deleted : bool = False
'''

def hashit(plain_text):
  
	result = hashlib.sha256(plain_text.encode())

	return result.hexdigest()


def do_signUp(user_attrs):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = db_con.cursor()

		if user_attrs is None or len(user_attrs) <= 0 :
			 return(RetCodes.missing_ent_attrs_error.value,"user attributes dictionary missing.", None)
		
		if 'email' not in user_attrs.keys():
			 return(RetCodes.missing_ent_attrs_error.value,"Email Id is missing.", None)
		
		if 'name' not in user_attrs.keys():
			 return(RetCodes.missing_ent_attrs_error.value,"User name is missing.", None)

		if 'status' not in user_attrs.keys():
			 return(RetCodes.missing_ent_attrs_error.value,"User status is missing.", None)

		if 'password' not in user_attrs.keys():
			 return(RetCodes.missing_ent_attrs_error.value,"User password is missing.", None)

		if 'tname' not in user_attrs.keys():
			 return(RetCodes.missing_ent_attrs_error.value,"Company is missing.", None)


		email = user_attrs['email'].strip()
		name = user_attrs['name'].strip()
		status = user_attrs['status']
		password = user_attrs['password'].strip()

		tname = user_attrs['tname'].strip()

		if not email:
			 return(RetCodes.empty_ent_attrs_error.value,"Email empty or null.", None)

		if not name:
			 return(RetCodes.empty_ent_attrs_error.value,"Name empty or null.", None)

		if not password:
			 return(RetCodes.empty_ent_attrs_error.value,"password empty or null.", None)

		if not tname:
			 return(RetCodes.empty_ent_attrs_error.value,"Company Name empty or null.", None)

		
		password = hashit(password)

		##insert a record in user table
		sql = """insert into users ( email, name, status, password,is_deleted) 
				values (%s,%s, %s,%s,%s) returning id """
		params = (email,name,status,password,False)
		print ( cursor.mogrify(sql, params))
		
		cursor.execute(sql, params)
		assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

		result = cursor.fetchone()
		uid = result[0]
		print ("user id created is",uid )

		## insert a record into tenant 
		sql = """insert into tenants ( name,status,is_deleted) 
			values (%s,%s, %s) returning id """
		params = (tname,0,False)
		print ( cursor.mogrify(sql, params))
	
		cursor.execute(sql, params)
		assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."
		result = cursor.fetchone()
		tid = result[0]
		print ("Tenant id created is",tid )

		## insert a record into tenant users table with isadmin field set to true
		sql = """insert into tenant_user_roles ( tid,uid,rid) 
			values (%s,%s, %s)  """
		params = (tid,uid,1)
		print ( cursor.mogrify(sql, params))
	
		cursor.execute(sql, params)
		assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."


		db_con.commit()

		return (RetCodes.success.value, "User sign up successful.", None)


	except Exception as e:
		print(e)
		db_con.rollback()
		return (RetCodes.server_error.value, str(e),None)
	
	finally:
		if cursor is not None:
			cursor.close()
		dbUtils.returnToPool(db_con)


def update_user(userID,update_attrs):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = db_con.cursor()

		if update_attrs is None or len(update_attrs) <= 0 :
			 return(RetCodes.missing_ent_attrs_error.value,"update attributes dictionary is missing.", None)
		#TODO: Check column key is valid key representing a column

		#hash the password 
		update_attrs['password'] = hashit(str(update_attrs['password']))

		if len(update_attrs) == 1:
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
			return (RetCodes.success.value, "User update successed.", updated_rows)
		else:
			db_con.rollback()
			return (RetCodes.save_ent_error.value, "User update failed as updated rows is <> 1", updated_rows)

	except Exception as e:
		print(e)
		db_con.rollback()
		return (RetCodes.server_error.value, str(e),None)
	
	finally:
		if cursor is not None:
			 cursor.close()
		dbUtils.returnToPool(db_con)



def delete_user(userID):
	try:
		
		db_con = dbUtils.getConnFromPool()		
		cursor = dbUtils.getNamedTupleCursor(db_con)

		sql = """UPDATE fl_iam_users SET is_deleted = %s WHERE id = %s"""		
		params = (True,userID)
		
		print (sql)		
		print ( cursor.mogrify(sql, params))

		cursor.execute(sql, params)
		updated_rows = cursor.rowcount

		db_con.commit()
		
		if updated_rows != 1 :
			return(RetCodes.del_ent_error.value, "DELETE for User ID '{0}' failed.".format(userID), updated_rows)
		else:
			return(RetCodes.success.value, "DELETE for User ID '{0}' succeeded.".format(userID),updated_rows)
	
	except Exception as e:
		print(e)
		return(RetCodes.server_error.value, str(e), None) 

	finally:
		if cursor is not None : 
			cursor.close()

		dbUtils.returnToPool(db_con)

def get_user(userID):
	
	try:
		
		db_con = dbUtils.getConnFromPool()		
		cursor = dbUtils.getNamedTupleCursor(db_con)

		sql = """SELECT * FROM fl_iam_users WHERE id = %s and is_deleted = %s """		
		params = (userID,False)
		
		print (sql)		
		print ( cursor.mogrify(sql, params))

		cursor.execute(sql, params)

		userList =cursor.fetchall()

		#if userList == None or len(userList) <= 0 :
		#	return(RetCodes.get_ent_error1.value, "User ID '{0}' not found in database".format(userID), None)

		if userList == None or len(userList) != 1 :
			return(RetCodes.get_ent_error.value, "Found '{0}' records for User ID '{1}' when 1 record was expected.".format(len(userList),userID), len(userList))

		for user in userList:
			print(user)

		return(RetCodes.success.value, "User ID '{0}' successfully fetched from db".format(userID), userList[0])
	
	except Exception as e:
		print(e)
		return(RetCodes.server_error.value, str(e), None) 

	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)

def list_users():
	
	try:
		
		db_con = dbUtils.getConnFromPool()		
		cursor = dbUtils.getNamedTupleCursor(db_con)

		sql = """SELECT * FROM fl_iam_users WHERE is_deleted = %s """		
		params = (False,)
		
		print (sql)		
		print ( cursor.mogrify(sql, params))

		cursor.execute(sql, params)

		userList =cursor.fetchall()

		for user in userList:
			print(user)

		return(RetCodes.success.value, "User List successfully fetched from db", userList)
	
	except Exception as e:
		print(e)
		return(RetCodes.server_error.value, str(e), None) 

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

def do_SignIn(id, password):
	
	try:
		password = hashit(password)

		try:
			db_con = dbUtils.getConnFromPool()
			cursor = dbUtils.getNamedTupleCursor(db_con)
			
			query = """SELECT * , 
					(select tid from tenant_user_roles where uid = id) FROM users WHERE
					email = %s and password = %s and is_deleted = %s"""
		
			data_tuple = (id, password, False)

			print ( cursor.mogrify(query, data_tuple))
			cursor.execute(query, data_tuple)

			userList =cursor.fetchall()
			print ( "user length ",len(userList))

			if (userList is None or len(userList) != 1) :
				return (RetCodes.sign_in_failed, 
				"Sign in failed as either no user with this email ID exists or wrong password has been provided.", 
				None)

			for user in userList:
				print(user)

			return(RetCodes.success.value, "User List successfully fetched from db", userList[0])


		except Exception as dbe:
			print(dbe)
			return ( RetCodes.server_error, str(dbe), None)
			#db_con.rollback()
			#raise
		
		finally:
			cursor.close()
			dbUtils.returnToPool(db_con)	

	except Exception as e:
		print ("In the exception block.")
		print(e)
		return ( RetCodes.server_error, str(e))




## main entry point
if __name__ == "__main__":
	#getUserConfigList('rrkanade22@yahoo.com','CAMI')
	#value = getUserConfig('rrkanade22@yahoo.com','CAMI', "email_server")
	#print(value)
	#getUsersForApp(constants.APP_CODE_CAMI)
	#getSummaryReportForToday( 'rrkanade22@yahoo.com' )
	
	(retCode, msg ) = signUp("Rajesh Kanade", "rrkanade@yahoo.com")
	#(retCode, msg, userRecord ) = get_user("rajesh")
	#(retCode, msg, userRecord ) = delete_user("rajesh")
	
	#(retCode, msg, userRecord ) = update_user("rk4",{'status':Status.active.value,'name':'rajesh hash', 'password':'hashit'})
	
	print( retCode)
	print ( msg)
	print ( userRecord)

	"""
	(retCode, msg, userRecord ) = update_user("rajesh",{'status':Status.active.value,'name':'rajesh python'})
	
	(retCode, msg, userRecord ) = update_user("rajesh",{})
	(retCode, msg, userRecord ) = update_user("rajesh",{'name':'vs code'})
	
	print( retCode)
	print ( msg)
	print ( userRecord)
	
	

	(retCode, msg, userRecord ) = delete_user('rk1')
	#(retCode, msg, userRecord ) = do_signUp({'id':'RK2','status':Status.active.value,'name':'R K 2','password':'dummy'})

	print( retCode)
	print ( msg)
	print ( userRecord)
	"""

	(retCode, msg, userRecord ) = do_signUp({'id':'rk5','name':'RK5','status':Status.active.value,'password':'pwd'})
	#(retCode, msg, userRecord ) = do_signUp({'id':'RK2','status':Status.active.value,'name':'R K 2','password':'dummy'})

	print( retCode)
	print ( msg)
	print ( userRecord)
	
	
	(retCode, msg, userList ) = list_users()
	print( retCode)
	print ( msg)
	for user in userList:
		print ( user)
	
	(retCode, msg, userList ) = get_user('rk1')
	print( retCode)
	print ( msg)
	