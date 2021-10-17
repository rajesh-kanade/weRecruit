from flask import (
	Flask,
	flash,
	g,
	redirect,
	render_template,
	request,
	session,
	url_for
)
from flask_session import Session
from webForms import JDForm, JDHeaderForm, SignUpForm , SignInForm
from turbo_flask import Turbo

import logging
import userUtils
import jdUtils
import constants
import functools

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

#turbo = Turbo(app)
Session(app)

logging.basicConfig(level=logging.DEBUG)

"""def cleanup(sender, **extra):
	print('inside Tearing down cleanup  function')
	session.close()

from flask import appcontext_tearing_down
appcontext_tearing_down.connect(cleanup, app)"""

@app.route('/')
def home():
	return render_template('index.html')        
		

@app.route('/user/showSigninPage')
def show_signin_page():
	form = SignInForm()
	return render_template('sign_in.html', form = form)

@app.route('/user/doSignin', methods = ['POST'])
def do_signin():

	form = SignInForm()

	results = userUtils.do_SignIn( form.email.data, form.password.data)

	if (results[0] == userUtils.RetCodes.success.value):        
		#flash (results[1],"is-info")
		user = results[2] 

		session["user_id"] = user.id  #form.email.data
		session["user_name"] = user.name #'Mr. Customer'

		#return render_template('home.html') 
		return redirect(url_for('show_home_page'))


	else:
		flash (results[1],"is-danger")
		return redirect('/user/showSigninPage')


@app.route('/user/showSignupPage')
def show_signup_page():
	form=SignUpForm()
	return render_template('sign_up.html', form = form)

@app.route('/user/createUser',  methods = ['POST'])
def create_user():

	form = SignUpForm()

	userAttrs = {}

	userAttrs['email'] = form.email.data
	userAttrs['password'] = form.password.data
	userAttrs['name'] = form.name.data
	userAttrs['status'] =userUtils.Status.active.value
	userAttrs['tname'] = form.company_name.data


	results = userUtils.create_user( userAttrs)

	if (results[0] == userUtils.RetCodes.success.value):        
		flash ("Congratulations!!! '{0}' successfully signed up. Get started by signing in now.".format(form.name.data), "is-info")
		#form.success = True
		#return render_template('sign_in.html', form = SignInForm())
		return redirect(url_for("show_signin_page"))
	else:
		flash (results[0] + ':' +results[1],"is-danger")
		return redirect(url_for("show_signup_page"))

def login_required(func):
	@functools.wraps(func)
	def secure_function(*args, **kwargs):
		if "user_id" not in session:
			flash ( "You are not authenticated. Please login to access this page.","is-danger")
			return redirect(url_for("show_signin_page"))

		return func(*args, **kwargs)

	return secure_function

@app.route('/showHomePage')
@login_required
def show_home_page():

	#form=JDCreateForm()
	return render_template('home.html')
	#return redirect('create_jd.html', form = form)
	#redirect('/user/showSigninPage')

@app.route('/user/doSignout', methods = ['GET'])
@login_required
def do_signout():

	session.clear()
	flash('Successfully logged out.',"is-info")
	return redirect('/user/showSigninPage') 
		
	'''if 'user_id' in session :
	#session.pop('user_id', None)
	#session.pop('user.name', None)
	session.clear()
	flash('Successfully logged out.',"is-info")
	return redirect('/user/showSigninPage')    
	else:
	return redirect(url_for('/'))'''

@app.route('/jd/showCreatePage', methods = ['GET'])
@login_required
def show_jd_create_page():
	form = JDForm()
	form.id.data = constants.NEW_ENTITY_ID
	return render_template('jd/edit.html', form=form)

@app.route('/jd/showAllPage', methods = ['GET'])
@login_required
def show_jd_all_page():
	results = jdUtils.list_jds(session.get('user_id'))
	if (results[0] == jdUtils.RetCodes.success.value): 
		print( 'success')
		jdList = results[2]    
		for jd in jdList:
			print(jd.title)   
		return render_template('jd/list.html', jdList = jdList )
	else:
		flash (results[0] + ':' +results[1],"is-danger")
		return render_template('jd/list.html',jdList = None)

@app.route('/jd/save', methods = ['POST'])
@login_required
def save_JD():

	print('inside create JD.')

	form = JDForm()

	loggedInUserID = session.get('user_id')
	print('JD id is {0}'.format(form.id.data))
	
	results = jdUtils.save_jd(form.id.data, form.title.data,form.details.data,
								form.client.data,int(loggedInUserID),jdUtils.JD_DEF_POSITIONS,form.open_date.data,
								form.intv_panel_name_1.data,form.intv_panel_email_1.data,form.intv_panel_phone_1.data,
								form.intv_panel_name_2.data,form.intv_panel_email_2.data,form.intv_panel_phone_2.data,
								form.hiring_mgr_name.data,form.hiring_mgr_email.data,form.hiring_mgr_phone.data,
								form.hr_name.data,form.hr_email.data,form.hr_phone.data)

	if (results[0] == jdUtils.RetCodes.success.value):        
		flash ("Congratulations!!! Job Requistion with title '{0}' successfully created".format(form.title.data), "is-info")
		return redirect(url_for("show_home_page"))
	else:
		flash (results[0] + ':' +results[1],"is-danger")
		return redirect(url_for("show_home_page"))

@app.route('/jd/showEditPage/<int:id>', methods = ['GET'])
@login_required
def show_jd_edit_page(id):

	print('inside edit JD page for Job ID : ' , id)

	#loggedInUserID = session.get('user_id')
	
	form = JDForm()
	form.id.data = id

	results = jdUtils.get(id)

	"""if 'show' in request.args:
		print('inside show')
		show = request.args.get('show')
	else:
		show="header" """
	if (results[0] == jdUtils.RetCodes.success.value):        
		
		jd = results[2]

		form.id.data = jd.id
		form.title.data = jd.title
		form.details.data = jd.details
		form.client.data = jd.client

		form.total_positions.data = jd.positions
		form.open_date.data = jd.open_date
		
		# TODO status field required
		# TODO positions field required

		form.intv_panel_name_1.data = jd.ip_name_1
		form.intv_panel_email_1.data = jd.ip_emailid_1
		form.intv_panel_phone_1.data = jd.ip_phone_1

		form.intv_panel_name_2.data = jd.ip_name_2
		form.intv_panel_email_2.data = jd.ip_emailid_2
		form.intv_panel_phone_2.data = jd.ip_phone_2

		form.hiring_mgr_name.data = jd.hiring_mgr_name
		form.hiring_mgr_email.data = jd.hiring_mgr_emailid
		form.hiring_mgr_phone.data = jd.hiring_mgr_phone

		form.hr_name.data = jd.hr_name
		form.hr_email.data = jd.hr_emailid
		form.hr_phone.data = jd.hr_phone

		return render_template('jd/edit.html', form=form)
	else:
		flash (results[0] + ':' +results[1],"is-danger")
		return redirect(url_for("show_home_page"))

	#return render_template('jd/edit.html', show= show, headerForm = form)

@app.route('/jd/saveHeader', methods = ['POST'])
@login_required
def jd_save_header():

	print('inside save header')

	form =  JDHeaderForm()
	print( form.id.data)
	print ( form.title.data)
	print ( form.details.data)
	print ( form.client.data)

	results = jdUtils.save_header(form.id.data,form.title.data,form.details.data,form.client.data)
	if (results[0] == jdUtils.RetCodes.success.value):
		flash (results[1], "is-success")
	else:
		flash (results[1], "is-danger")
	
	#return "saved successful."
	return render_template('jd/header.html', headerForm = form)
	#return redirect(url_for('show_jd_edit_page'), id = form.id.data)


if __name__ == "__main__":
	app.run()