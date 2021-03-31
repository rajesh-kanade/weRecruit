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
#import json
import decimal


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
			return jsonify({'retcode': -101}, {'msg': 'POST method not found.'}),400
		
		if ('email' in request.json == False):
			return jsonify({'retcode': -102}, {'msg': 'Email parameter not found in request. '}),400

		(retCode,msg) = userUtils.getOTP(str(request.json['email']))
		
		return jsonify({'retcode': retCode}, {'msg': msg})

	except Exception as e:
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -110},{'msg':str(e)}) ,400


@app.route('/v1/signUp', methods = ['POST'])
def userSignUp():
	error = ''
	try:
		assert request.method == "POST", "Unsupported request method. Only POST supported."
		assert 'username'  in request.json , "User ID not found in request json."
		assert 'email'  in request.json , "User ID not found in request json."

		print('**** Processing POST request **********')
		print(request.json)			
		
		new_username = str(request.json['username'])
		print ( new_username)

		new_email = str(request.json['email'])
		print ( new_email)


		(retCode,msg) = userUtils.signUp(new_username,new_email)			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) , 400


@app.route('/v1/authenticate', methods = ['POST'])
def authenticate():
	error = ''
	try:
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		print('**** Processing POST request **********')
		
		assert 'Email'  in request.json , "Email not found in request json."
		assert 'OTP' in request.json, "OTP not found in request json."

		#if userID exists in request.json == false :
		#	raise 
		email = request.json['Email']
		print ( email)

		otp = request.json['OTP']
		print ( otp)
		
		(retCode,msg) = userUtils.userSignIn(email,otp)			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) , 400

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/v1/productAdd', methods = ['POST'])
def productAdd():
	error = ''
	try:
		
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		assert 'productID'  in request.json , "Product ID not found in request json."
		assert 'unitPrice'  in request.json , "Unit Price not found in request json."
		assert 'currency' in request.json , "Currency Price not found in request json."
		#assert 'billingFrequency' in request.form , "Billing Frequency not found in request json."

		print('**** Processing POST request **********')
		#print(request.json)			
		
		productID = str(request.json['productID'])
		print ( productID)

		unitPrice = str(request.json['unitPrice'])
		print ( unitPrice)

		currency = str(request.json['currency'])
		print ( currency)			

		(retCode,msg) = productUtils.add_product(productID, unitPrice,currency)
			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) 

@app.route('/v1/deactivateProduct', methods = ['POST'])
def deactivateProduct():
	error = ''
	try:		
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		#assert 'productID'  in request.query_string , "Product ID not found in request json."

		print('**** Processing POST request **********')
		assert request.method == "POST", "Unsupported request method. Only POST supported."
		assert 'productID'  in request.json , "Product ID not found in request json."

		productID = request.json['productID']


		(retCode,msg) = productUtils.update_product(productID, 
				{'status' : productUtils.PRODUCT_STATUS_INACTIVE} )
			
		return jsonify({'retcode': retCode},{'msg': 'Product deactivated successfully.'})

	except Exception as e:
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) ,400

@app.route('/v1/getProducts', methods = ['POST'])
def getProducts():
	error = ''
	try:
		
		assert request.method == "POST", "Unsupported request method. Only POST supported."


		print('**** Processing POST request **********')
		#print(request.json)			
		
		(retCode,msg, result) = productUtils.list_products()

		return jsonify({'retcode': retCode},{'msg': msg}, {'result': result})
		#return jsonify(json.dumps(result, cls=CustomEncoder))

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) ,400

@app.route('/v1/createCart', methods = ['POST'])
def createCart():
	error = ''
	try:
		
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		assert 'cartID'  in request.json , "cart ID not found in request json."

		print('**** Processing POST request **********')
		#print(request.json)			
		
		cartID = str(request.json['cartID'])
		(retCode,msg) = productUtils.create_cart(cartID)
			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) ,400

@app.route('/v1/addProductToCart', methods = ['POST'])
def addProductToCart():
	error = ''
	try:
		
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		assert 'cartID'  in request.json , "cartID not found in request json."
		assert 'productID'  in request.json , "productID not found in request json."

		print('**** Processing POST request **********')
		#print(request.json)			
		
		cartID = str(request.json['cartID'])
		productID = str(request.json['productID'])

		(retCode,msg) = productUtils.add_product_to_cart(cartID,productID)
			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) ,400


@app.route('/v1/removeProductFromCart', methods = ['POST'])
def removeProductFromCart():
	error = ''
	try:
		
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		assert 'cartID'  in request.json , "cartID not found in request json."
		assert 'productID'  in request.json , "productID not found in request json."

		print('**** Processing POST request **********')
		#print(request.json)			
		
		cartID = str(request.json['cartID'])
		productID = str(request.json['productID'])

		(retCode,msg) = productUtils.remove_product_from_cart(cartID,productID)
			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) ,400

@app.route('/v1/getCartDetails', methods = ['POST'])
def getCartDetails():
	error = ''
	try:
		
		assert request.method == "POST", "Unsupported request method. Only POST supported."

		assert 'cartID'  in request.json , "cartID not found in request json."

		print('**** Processing POST request **********')
		
		cartID = str(request.json['cartID'])

		(retCode,msg,result) = productUtils.get_cart_details(cartID)
		return jsonify({'retcode': retCode},{'msg': msg}, {'result': result})
		
	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) ,400

@app.route('/v1/checkoutCart', methods = ['POST'])
def checkoutCart():
	error = ''
	try:		
		assert request.method == "POST", "Unsupported request method. Only POST supported."
		assert 'cartID'  in request.json , "cartID not found in request json."

		#assert 'productID'  in request.query_string , "Product ID not found in request json."

		print('**** Processing POST request **********')

		cartID = request.json['cartID']

		print ( cartID)

		(retCode,msg) = productUtils.checkout_cart(cartID ) 
			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) , 400

# driver function 
if __name__ == '__main__': 
	app.run(debug = True, port=4000) 
