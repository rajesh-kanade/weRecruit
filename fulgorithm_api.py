from flask import Flask, jsonify, request 

from flask_cors import CORS


import userUtils

import os

app = Flask(__name__) 
CORS(app)

@app.route('/api/Authenticate', methods = ['GET'])
def authenticate():
	error = ''
	try:
		assert request.method == "GET", "Unsupported request method. Only GET supported."

		print('**** Processing GET request **********')
		
		assert 'userID'  in request.args , "User ID parameter not found in request."
		assert 'PWD' in request.args, "Password request parameter not found in request."

		#if userID exists in request.json == false :
		#	raise 
		userID = request.args.get("userID") #request.json['userID']
		print ( userID)

		pwd = request.args.get("PWD") #request.json['PWD']
		print ( pwd)
		
		(retCode,msg) = userUtils.userSignIn(userID,pwd)			
		return jsonify({'retcode': retCode},{'msg': msg})

	except Exception as e:
		#flash(e)
		print ("In the exception block.")
		print(e)
		return jsonify({'retcode': -101},{'msg': str(e)}) , 400


# driver function 
if __name__ == '__main__': 
	app.run(debug = True, port=4000) 
