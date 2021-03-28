from flask import Flask, jsonify, request 

import random
from flask_mail import Mail, Message 
from flask_cors import CORS

import constants
import userUtils
import emailUtils
from jinja2 import Environment, FileSystemLoader
from werkzeug.utils import secure_filename

import productUtils

import os

ALLOWED_EXTENSIONS = {'pdf', 'docx'}


app = Flask(__name__) 
CORS(app)

mail = Mail(app) # instantiate the mail class 
   
# configuration of mail 

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '43476df397bb98'
app.config['MAIL_PASSWORD'] = '549b9cb128c807'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['UPLOAD_FOLDER'] = './temp'

mail = Mail(app) 


@app.route('/v1/getOTP', methods = ['POST']) 	
def getOTP():
	try:
		print('**** Processing POST request **********')
		print(request.json)	

		if request.method != "POST":
			return jsonify({'retcode': -101}, {'msg': 'POST method not found.'})
		
		if ('email' in request.json == False):
			return jsonify({'retcode': -102}, {'msg': 'Email parameter not found in request. '})

		(retCode,msg) = userUtils.getOTP(str(request.json['email']))
		
		return jsonify({'retcode': retCode}, {'msg': msg})

	except Exception as e:
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -110},{'msg':str(e)}) 


@app.route('/v1/signUp', methods = ['POST'])
def userSignUp():
	error = ''
	try:
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		print('**** Processing POST request **********')
		print(request.json)			
		
		new_username = str(request.json['username'])
		print ( new_username)

		new_email = str(request.json['email'])
		print ( new_email)

		new_appcode = str(request.json['appcode'])
		print ( new_appcode)			

		(retCode,msg) = userUtils.signUp(new_email,new_username,new_appcode)			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) 


@app.route('/v1/signIn', methods = ['POST'])
def userSignIn():
	error = ''
	try:
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		print('**** Processing POST request **********')
		print(request.json)			
		
		assert 'userID'  in request.json , "User ID not found in request json."
		assert 'OTP' in request.json, "OTP not found in request json."

		#if userID exists in request.json == false :
		#	raise 
		userID = request.json['userID']
		print ( userID)

		otp = request.json['OTP']
		print ( otp)
		
		
		try:
			db_con = sqlite3.connect(constants.DB_NAME)
			cursor = db_con.cursor()

			#insert into user table
			query = """SELECT COUNT(*) FROM user WHERE
					ID = ? and OTP = ? """
		
			data_tuple = (str(userID), str(otp))

			print (query)
			cursor.execute(query, data_tuple)
			(number_of_rows,)=cursor.fetchone()
			print ( "No of rows returned : " +str(number_of_rows))

			if (number_of_rows) == 1 :
				return jsonify({'retcode': 0},{'msg': 'login Successful'})
			else:
				return jsonify({'retcode': -1},{'msg': 'login failed'})
				

		except Exception as dbe:
			print(dbe)
			#db_con.rollback()
			raise
		finally:
			cursor.close()
			db_con.close()	

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/v1/productAdd', methods = ['POST'])
def productAdd():
	error = ''
	try:
		
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		assert 'productID'  in request.form , "Product ID not found in request json."
		assert 'unitPrice'  in request.form , "Unit Price not found in request json."
		assert 'currency' in request.form , "Currency Price not found in request json."
		#assert 'billingFrequency' in request.form , "Billing Frequency not found in request json."

		print('**** Processing POST request **********')
		#print(request.json)			
		
		productID = str(request.form['productID'])
		print ( productID)

		unitPrice = str(request.form['unitPrice'])
		print ( unitPrice)

		currency = str(request.form['currency'])
		print ( currency)			

		(retCode,msg) = productUtils.product_add(productID, unitPrice,currency)
			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) 

# driver function 
if __name__ == '__main__': 
	app.run(debug = True, port=4000) 
