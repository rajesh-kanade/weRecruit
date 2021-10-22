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
from webForms import ResumeShortlistForm, ResumeForm, JDApply, JDForm, JDHeaderForm, SignUpForm , SignInForm
from turbo_flask import Turbo
from werkzeug.utils import secure_filename
from flask import send_file

import logging
import userUtils
import jdUtils
import constants
import resumeUtils
import functools
import os

from datetime import datetime
from datetime import timezone 

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

UPLOAD_FOLDER = '\\resume_uploads'  #TODO win specific for now. Take care of path sep on linux
ALLOWED_EXTENSIONS = {'doc', 'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
	form.total_positions.data = jdUtils.JD_DEF_POSITIONS	
	form.status.data = jdUtils.JDStatusCodes.open.value

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

	print('inside save JD.')

	form = JDForm()

	loggedInUserID = session.get('user_id')
	print('JD id is {0}'.format(form.id.data))
	
	results = jdUtils.save_jd(form.id.data, form.title.data,form.details.data,
								form.client.data,int(loggedInUserID),int(form.total_positions.data),form.open_date.data,
								form.intv_panel_name_1.data,form.intv_panel_email_1.data,form.intv_panel_phone_1.data,
								form.intv_panel_name_2.data,form.intv_panel_email_2.data,form.intv_panel_phone_2.data,
								form.hiring_mgr_name.data,form.hiring_mgr_email.data,form.hiring_mgr_phone.data,
								form.hr_name.data,form.hr_email.data,form.hr_phone.data,
								int(form.status.data))

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
		form.status.data = jd.status

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

@app.route('/jd/showApplyPage/<int:id>', methods = ['GET'])
@login_required
def show_jd_apply_page(id):

	print('inside apply JD page for Job ID : ' , id)
	
	form = JDApply()

	form.jd_id.data = id
	form.resume_id.data = constants.NEW_ENTITY_ID
	form.jd_title.data = 'Test Title'

	return render_template('jd/apply.html',form=form)

@app.route('/jd/apply', methods = ['POST'])
@login_required
def apply_to_JD():

	print('inside apply to JD.')

	form = JDApply()

	loggedInUserID = session.get('user_id')
	print('JD id is {0}'.format(form.jd_id.data))
	print('candidate name is {0}'.format(form.candidate_name.data))
	print('candidate email is {0}'.format(form.candidate_email.data))
	print('candidate phone is {0}'.format(form.candidate_phone.data))
	print('candidate resume file name is {0}'.format(form.candidate_resume.data))


	'''results = jdUtils.appy_to_jd(form.id.data, form.title.data,form.details.data,
								form.client.data,int(loggedInUserID),int(form.total_positions.data),form.open_date.data,
								form.intv_panel_name_1.data,form.intv_panel_email_1.data,form.intv_panel_phone_1.data,
								form.intv_panel_name_2.data,form.intv_panel_email_2.data,form.intv_panel_phone_2.data,
								form.hiring_mgr_name.data,form.hiring_mgr_email.data,form.hiring_mgr_phone.data,
								form.hr_name.data,form.hr_email.data,form.hr_phone.data,
								int(form.status.data))
	'''

	if form.validate_on_submit():
		f = form.candidate_resume.data
		filename = secure_filename(f.filename)
		print( app.instance_path)
		print(filename)
		f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		f.save(filename)

		resumeUtils.save_resume(constants.NEW_ENTITY_ID, filename,form.candidate_name.data,
								form.candidate_email.data,form.candidate_phone,int(session.get('user_id')))
		return redirect(url_for("show_home_page"))
	else:
		return render_template('jd/apply.html', form= form)
		
	'''if (results[0] == jdUtils.RetCodes.success.value):        
		flash ("Congratulations!!! Job Requistion with title '{0}' successfully created".format(form.title.data), "is-info")
		return redirect(url_for("show_home_page"))
	else:
		flash (results[0] + ':' +results[1],"is-danger")
		return redirect(url_for("show_home_page"))
	'''
@app.route('/resume/showUploadPage', methods = ['GET'])
@login_required
def show_resume_upload_page():
	form = ResumeForm()
	
	form.id.data = constants.NEW_ENTITY_ID
	#form.status.data = jdUtils.JDStatusCodes.open.value

	return render_template('resume/edit.html', form=form)

@app.route('/resume/save', methods = ['POST'])
@login_required
def resume_save():

	print('inside resume save.')

	form = ResumeForm()

	loggedInUserID = session.get('user_id')
	print('Resume id is {0}'.format(form.id.data))
	print('candidate name is {0}'.format(form.candidate_name.data))
	print('candidate email is {0}'.format(form.candidate_email.data))
	print('candidate phone is {0}'.format(form.candidate_phone.data))
	print('candidate resume file name is {0}'.format(form.candidate_resume.data))

	if form.validate_on_submit():
		f = form.candidate_resume.data
		filename = secure_filename(f.filename)
		print('app root path is {0}'.format(app.root_path))
		#resource_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
		#print ( 'resource path is {0}'.format(resource_path))
		#f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		f.save(os.path.join(app.root_path + UPLOAD_FOLDER, filename))

		#f.save(resource_path,filename)
		f.close()

		results = resumeUtils.save_resume(constants.NEW_ENTITY_ID, filename,form.candidate_name.data,
								form.candidate_email.data,form.candidate_phone.data,int(session.get('user_id')))
		if results[0] == resumeUtils.RetCodes.success.value:
			return redirect(url_for("show_home_page"))
		else:
			flash (results[0] + ':' +results[1],"is-danger")
			form.submit.errors.append(results[1])
			return render_template('resume/edit.html', form= form)	
	else:
		return render_template('resume/edit.html', form= form)
		
	'''if (results[0] == jdUtils.RetCodes.success.value):        
		flash ("Congratulations!!! Job Requistion with title '{0}' successfully created".format(form.title.data), "is-info")
		return redirect(url_for("show_home_page"))
	else:
		flash (results[0] + ':' +results[1],"is-danger")
		return redirect(url_for("show_home_page"))
	'''

@app.route('/resume/showBrowser', methods = ['GET'])
@login_required
def show_resume_browser_page():
	results = resumeUtils.list_resumes(session.get('user_id'))
	if (results[0] == resumeUtils.RetCodes.success.value): 
		print( 'success')
		resumeList = results[2]    
		for resume in resumeList:
			print(resume.name)   
		return render_template('resume/list.html', resumeList = resumeList )
	else:
		flash (results[0] + ':' +results[1],"is-danger")
		return render_template('resume/list.html',resumeList = None)

@app.route('/resume/showEditPage/<int:id>', methods = ['GET'])
@login_required
def show_resume_edit_page(id):

	print('inside edit resume page for  ID {0} '.format(id))

	#loggedInUserID = session.get('user_id')
	
	form = ResumeForm()
	form.id.data = id

	results = resumeUtils.get(id)


	if (results[0] == resumeUtils.RetCodes.success.value):        
		
		#resume = results[2]

		form.id.data = results[2].id
		form.candidate_name.data = results[2].name
		form.candidate_email.data = results[2].email
		form.candidate_phone.data = results[2].phone
		form.candidate_resume.data = results[2].resume_filename

		return render_template('resume/edit.html', form=form)
	else:
		flash (results[0] + ':' +results[1],"is-danger")
		return redirect(url_for("show_home_page"))

@app.route('/resume/download', methods = ['GET'])
@login_required
def resume_download():
	assert request.args['resume'], "Did not find resume key in request parameters."
	
	filename = request.args['resume']
	path = os.path.join(app.root_path + UPLOAD_FOLDER, filename)

	return send_file(path, as_attachment=True)

@app.route('/resume/showshortlistpage', methods = ['GET'])
@login_required
def show_resume_shortlist_page():

	print('inside shortlist resume page for  ID {0} '.format(id))

	assert request.args.get('id'), "Resume ID request parameter not found."
	assert request.args.get('name'), "Candidate Name request parameter not found."

	form = ResumeShortlistForm()
	form.id.data = request.args.get('id')
	form.candidate_name.data = request.args.get('name')

	results = jdUtils.list_jds(session.get('user_id'))

	if (results[0] == jdUtils.RetCodes.success.value): 
		jdList = results[2]    
		for jd in jdList:
			print(jd.title)
		form.selected_jd_list.choices = [(jd.id, jd.title + " | " + str(jd.id)) for jd in jdList]
		return render_template('resume/shortlist.html', form=form)		   
	else:
		flash (results[0] + ':' +results[1],"is-danger")
		return render_template('resume/shortlist.html',form = form)


@app.route('/resume/shortlist', methods = ['POST'])
@login_required
def resume_shortlist():

	print('inside resume shortlist.')

	form = ResumeShortlistForm()

	loggedInUserID = session.get('user_id')
	print('Resume id is {0}'.format(form.id.data))
	print('Selected JD List is {0}'.format(form.selected_jd_list.data))

	#if form.validate_on_submit():
	print('inside validate true')
	results = resumeUtils.shortlist( form.id.data, form.selected_jd_list.data,
				datetime.now(tz=timezone.utc),resumeUtils.ApplicationStatusCodes.shortlisted.value, 
				loggedInUserID)

	if results[0] == resumeUtils.RetCodes.success.value:
		flash (results[0] + ':' +results[1],"is-success")
		return redirect(url_for("show_resume_browser_page"))
		#return render_template('resume/shortlist.html', form= form)	

	else:
		flash (results[0] + ':' +results[1],"is-danger")
		#form.submit.errors.append(results[1])
		return redirect(url_for("show_resume_browser_page"))
	#else:
	#	return render_template('resume/shortlist.html', form= form)



if __name__ == "__main__":
	app.run()