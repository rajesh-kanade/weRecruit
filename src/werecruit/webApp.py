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
from webForms import ResumeSearchForm, UserForm, ResetPasswordForm, ApplicationStatusUpdate, ResumeShortlistForm, ResumeForm, JDApply, JDForm, JDHeaderForm, SignUpForm, SignInForm, UserForm
from turbo_flask import Turbo
from werkzeug.utils import secure_filename
from flask import send_file
from flask_fontawesome import FontAwesome

import userUtils
import jdUtils
import constants
import resumeUtils
import reports
import emailUtils

import functools
import os

from jinja2 import Environment, FileSystemLoader

from datetime import datetime
from datetime import timezone
from datetime import timedelta

from dotenv import load_dotenv, find_dotenv

import logging
from logging.handlers import TimedRotatingFileHandler

from flask_paginate import Pagination, get_page_parameter, get_per_page_parameter

load_dotenv(find_dotenv())
logging.basicConfig(filename=constants.LOG_FILENAME_WEB, format=constants.LOG_FORMAT,
                    level=int(os.environ.get("LOG_LEVEL", 20)))

_logger = logging.getLogger()

app = Flask(__name__)

# print(os.environ.get("FLASK_SESSION_API_KEY"))
app.secret_key = os.environ.get("FLASK_SESSION_API_KEY", '')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

UPLOAD_FOLDER = '/temp'  # TODO win specific for now. Take care of path sep on linux
ALLOWED_EXTENSIONS = {'doc', 'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

turbo = Turbo(app)
Session(app)
fa = FontAwesome(app)


"""def cleanup(sender, **extra):
	_logger.debug('inside Tearing down cleanup  function')
	session.close()

from flask import appcontext_tearing_down
appcontext_tearing_down.connect(cleanup, app)"""


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/website/show_release_history')
def show_release_history_page():
    return render_template('/website/release_history.html')


@app.route('/user/showSigninPage')
def show_signin_page():
    form = SignInForm()
    return render_template('sign_in.html', form=form)


@app.route('/user/doSignin', methods=['POST'])
def do_signin():

    form = SignInForm()

    (retCode, msg, user) = userUtils.do_SignIn(
        form.email.data, form.password.data)

    if (retCode == userUtils.RetCodes.success.value):
        #flash (results[1],"is-info")
        #user = results[2]
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=15)

        # session.
        session["user_id"] = user.id  # form.email.data
        session["user_name"] = user.name  # 'Mr. Customer'
        session["tenant_id"] = user.tid
        session["email_id"] = user.email
        session["role_id"] = user.rid
        return redirect(url_for('show_home_page'))

    else:
        flash(msg, "is-danger")
        return redirect('/user/showSigninPage')


@app.route('/user/showSignupPage')
def show_signup_page():
    form = SignUpForm()
    return render_template('sign_up.html', form=form)


@app.route('/user/signUp',  methods=['POST'])
def sign_up():

    form = SignUpForm()

    userAttrs = {}

    userAttrs['email'] = form.email.data
    userAttrs['password'] = form.password.data
    userAttrs['name'] = form.name.data
    userAttrs['status'] = userUtils.Status.active.value
    userAttrs['tname'] = form.company_name.data

    results = userUtils.do_signUp(userAttrs)

    if (results[0] == userUtils.RetCodes.success.value):
        flash("Congratulations!!! '{0}' successfully signed up. Get started by signing in now.".format(
            form.name.data), "is-info")
        #form.success = True
        # return render_template('sign_in.html', form = SignInForm())
        return redirect(url_for("show_signin_page"))
    else:
        flash(results[0] + ':' + results[1], "is-danger")
        return redirect(url_for("show_signup_page"))


def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "user_id" not in session:
            flash(
                "You are not authenticated. Please login to access this page.", "is-danger")
            return redirect(url_for("show_signin_page"))

        return func(*args, **kwargs)

    return secure_function


@app.route('/showHomePage')
@login_required
def show_home_page():

    return render_template('home.html')


@app.route('/user/doSignout', methods=['GET'])
@login_required
def do_signout():

    session.clear()
    # TODO figure out if session pop is required for each session variable
    flash('Successfully logged out.', "is-info")
    return redirect('/user/showSigninPage')

    '''if 'user_id' in session :
	#session.pop('user_id', None)
	#session.pop('user.name', None)
	session.clear()
	flash('Successfully logged out.',"is-info")
	return redirect('/user/showSigninPage')    
	else:
	return redirect(url_for('/'))'''


@app.route('/jd/showCreatePage', methods=['GET'])
@login_required
def show_jd_create_page():
    form = JDForm()

    form.id.data = constants.NEW_ENTITY_ID
    form.total_positions.data = jdUtils.JD_DEF_POSITIONS
    form.status.data = jdUtils.JDStatusCodes.open.value

    return render_template('jd/edit.html', form=form)


@app.route('/jd/showAllPage', methods=['GET'])
@login_required
def show_jd_all_page():
    orderBy = request.args.get('order_by', None)
    order = request.args.get('order', None)

    toggles = {'client': {'arrowToggle': 'fa fa-arrow-down' if (orderBy == 'client' and order == 'ASC') else 'fa fa-arrow-up',
                          'orderToggle': 'DESC' if order == 'ASC' else 'ASC'},
               'status': {'arrowToggle': 'fa fa-arrow-down' if (orderBy == 'status' and order == 'ASC') else 'fa fa-arrow-up',
                          'orderToggle': 'DESC' if order == 'ASC' else 'ASC'},

               'title': {'arrowToggle': 'fa fa-arrow-down' if (orderBy == 'title' and order == 'ASC') else 'fa fa-arrow-up',
                         'orderToggle': 'DESC' if order == 'ASC' else 'ASC'},
               'open_date': {'arrowToggle': 'fa fa-arrow-down' if (orderBy == 'open_date' and order == 'ASC') else 'fa fa-arrow-up',
                             'orderToggle': 'DESC' if order == 'ASC' else 'ASC'},
               'hiring_mgr_name': {'arrowToggle': 'fa fa-arrow-down' if (orderBy == 'hiring_mgr_name' and order == 'ASC') else 'fa fa-arrow-up',
                                   'orderToggle': 'DESC' if order == 'ASC' else 'ASC'}
               }

    # 1 for up 0 for down
    # 1 for ASC 0 for DESC

    results = jdUtils.list_jds_by_tenant(
        session.get('tenant_id'), orderBy=orderBy, order=order)
    # print(orderBy)
    if (results[0] == jdUtils.RetCodes.success.value):
        jdList = results[2]

        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = request.args.get(
            get_per_page_parameter(), type=int, default=constants.PAGE_SIZE)
        # page, per_page, offset = get_page_args(page_parameter='page',
        #                                        per_page_parameter='per_page')
        offset = (page - 1) * per_page
        total = len(jdList)

        def getPages(offset=0, per_page=1):
            return jdList[offset: offset + per_page]
        pagination_JDList = getPages(offset=offset, per_page=per_page)
        # print(offset, per_page, page)
        pagination = Pagination(page=page, per_page=per_page, total=total,
                                css_framework='bootstrap4')
        pagination = Pagination(
            page=page, per_page=per_page,   total=total, css_framework='bootstrap4')
        for jd in jdList:
            _logger.debug(jd.title)
        return render_template('jd/list.html', jdList=pagination_JDList, request=request, page=page, per_page=1, pagination=pagination, toggles=toggles)
    else:
        flash(results[0] + ':' + results[1], "is-danger")
        return render_template('jd/list.html', jdList=None)


@app.route('/jd/save', methods=['POST'])
@login_required
def save_JD():

    _logger.debug('inside save JD.')

    form = JDForm(request.form)

    '''if request.method == 'POST' and form.max_yrs_of_exp.validate(form) is False:
		_logger.debug('JD save validation failed') 
		print(form.errors)
		return render_template('jd/edit.html', form=form)
	'''

    loggedInUserID = session.get('user_id')
    _logger.debug('JD id is {0}'.format(form.id.data))

    if form.client_jd.data != None:
        f = form.client_jd.data
        filename = secure_filename(f.filename)
        _logger.debug('app root path is {0}'.format(app.root_path))
        filename = os.path.join(app.root_path + UPLOAD_FOLDER, filename)
        f.save(filename)
        f.close()
    else:
        filename = None

    results = jdUtils.save_jd(form.id.data, form.title.data, form.details.data,
                              form.client.data, int(loggedInUserID), int(
                                  form.total_positions.data), form.open_date.data,
                              form.intv_panel_name_1.data, form.intv_panel_email_1.data, form.intv_panel_phone_1.data,
                              form.intv_panel_name_2.data, form.intv_panel_email_2.data, form.intv_panel_phone_2.data,
                              form.hiring_mgr_name.data, form.hiring_mgr_email.data, form.hiring_mgr_phone.data,
                              form.hr_name.data, form.hr_email.data, form.hr_phone.data,
                              int(form.status.data),
                              form.location.data, form.min_yrs_of_exp.data, filename,
                              form.primary_skills.data, form.secondary_skills.data,
                              form.ctc_min.data, form.ctc_max.data, form.ctc_currency.data,
                              form.fees_percent.data, form.warranty_in_months.data,
                              form.max_yrs_of_exp.data)

    if filename is not None and os.path.exists(filename):
        os.remove(filename)
    if (results[0] == jdUtils.RetCodes.success.value):
        flash("Congratulations!!! Job Requistion with title '{0}' successfully created".format(
            form.title.data), "is-info")
        return redirect(url_for("show_jd_all_page"))

    else:
        flash(results[0] + ':' + results[1], "is-danger")
        _logger.debug(results[0]+":"+results[1])
        # return redirect(url_for("show_jd_edit_page", id=form.id.data))
        errorList = list(form.id.errors)
        errorList.append(results[0] + ':' + results[1])
        form.id.errors = tuple(errorList)
        _logger.debug(form.max_yrs_of_exp.errors)
        #form.max_yrs_of_exp.errors = tuple(list(form.max_yrs_of_exp.errors).append( 'Error from backend'))
        # form.max_yrs_of_exp.errors.append()
        return render_template('jd/edit.html', form=form), 409
        # return redirect


@app.route('/jd/showEditPage/<int:id>', methods=['GET'])
@login_required
def show_jd_edit_page(id):

    _logger.debug('inside edit JD page for Job ID {0} '.format(id))

    #loggedInUserID = session.get('user_id')

    form = JDForm()
    form.id.data = id

    results = jdUtils.get(id)

    """if 'show' in request.args:
		_logger.debug('inside show')
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

        form.location.data = jd.location

        form.min_yrs_of_exp.data = jd.min_yrs_of_exp
        form.max_yrs_of_exp.data = jd.max_yrs_of_exp

        form.client_jd.data = jd.jd_file_name

        form.primary_skills.data = jd.primary_skills
        form.secondary_skills.data = jd.secondary_skills

        form.ctc_min.data = jd.ctc_min
        form.ctc_max.data = jd.ctc_max
        form.ctc_currency.data = jd.ctc_currency

        form.fees_percent.data = jd.fees_in_percent
        form.warranty_in_months.data = jd.warranty_period_in_months

        return render_template('jd/edit.html', form=form)
    else:
        flash(results[0] + ':' + results[1], "is-danger")
        return redirect(url_for("show_home_page"))

    # return render_template('jd/edit.html', show= show, headerForm = form)


@app.route('/jd/saveHeader', methods=['POST'])
@login_required
def jd_save_header():

    _logger.debug('inside save header')

    form = JDHeaderForm()
    _logger.debug(form.id.data)
    _logger.debug(form.title.data)
    _logger.debug(form.details.data)
    _logger.debug(form.client.data)

    results = jdUtils.save_header(
        form.id.data, form.title.data, form.details.data, form.client.data)
    if (results[0] == jdUtils.RetCodes.success.value):
        flash(results[1], "is-success")
    else:
        flash(results[1], "is-danger")

    # return "saved successful."
    return render_template('jd/header.html', headerForm=form)
    # return redirect(url_for('show_jd_edit_page'), id = form.id.data)


@app.route('/jd/showApplyPage/<int:id>', methods=['GET'])
@login_required
def show_jd_apply_page(id):

    _logger.debug('inside apply JD page for Job ID : ', id)

    form = JDApply()

    form.jd_id.data = id
    form.resume_id.data = constants.NEW_ENTITY_ID
    form.jd_title.data = 'Test Title'

    return render_template('jd/apply.html', form=form)


@app.route('/jd/apply', methods=['POST'])
@login_required
def apply_to_JD():

    _logger.debug('inside apply to JD.')

    form = JDApply()

    loggedInUserID = session.get('user_id')
    _logger.debug('JD id is {0}'.format(form.jd_id.data))
    _logger.debug('candidate name is {0}'.format(form.candidate_name.data))
    _logger.debug('candidate email is {0}'.format(form.candidate_email.data))
    _logger.debug('candidate phone is {0}'.format(form.candidate_phone.data))
    _logger.debug('candidate resume file name is {0}'.format(
        form.candidate_resume.data))

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
        _logger.debug(app.instance_path)
        _logger.debug(filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        f.save(filename)

        resumeUtils.save_resume(constants.NEW_ENTITY_ID, filename, form.candidate_name.data,
                                form.candidate_email.data, form.candidate_phone,
                                int(session.get('user_id')))
        return redirect(url_for("show_home_page"))

    else:
        return render_template('jd/apply.html', form=form)


@app.route('/resume/showUploadPage', methods=['GET'])
@login_required
def show_resume_upload_page():
    form = ResumeForm()

    form.id.data = constants.NEW_ENTITY_ID
    form.referrer.data = url_for(
        'show_resume_browser_page')  # request.referrer

    return render_template('resume/edit.html', form=form)


@app.route('/resume/showUploadPageViaEmail', methods=['GET'])
@login_required
def show_resume_upload_via_email_page():

    return render_template('resume/show_resume_upload_via_email_page.html')


@app.route('/resume/save', methods=['POST'])
@login_required
def resume_save():

    _logger.debug('inside resume save.')

    form = ResumeForm()

    loggedInUserID = session.get('user_id')
    _logger.debug('Resume id is {0}'.format(form.id.data))
    _logger.debug('candidate name is {0}'.format(form.candidate_name.data))
    _logger.debug('candidate email is {0}'.format(form.candidate_email.data))
    _logger.debug('candidate phone is {0}'.format(form.candidate_phone.data))
    _logger.debug('candidate resume file name is {0}'.format(
        form.candidate_resume.data))

    if form.candidate_resume.data != None:
        f = form.candidate_resume.data
        filename = secure_filename(f.filename)
        _logger.debug('app root path is {0}'.format(app.root_path))
        filename = os.path.join(app.root_path + UPLOAD_FOLDER, filename)
        f.save(filename)
        f.close()
    else:
        filename = None

    (retCode, msg, data) = resumeUtils.save_resume(form.id.data, filename, form.candidate_name.data,
                                                   form.candidate_email.data, form.candidate_phone.data, int(session.get('user_id')))

    if filename is not None and os.path.exists(filename):
        os.remove(filename)
    if retCode == resumeUtils.RetCodes.success.value:
        flash(msg, "is-success")
        # return redirect(url_for('show_resume_browser_page'))
        _logger.debug("Referrer to resume/save was %s", form.referrer.data)
        return redirect(form.referrer.data)

    else:
        flash(retCode + ':' + msg, "is-danger")
        return render_template('resume/edit.html', form=form)


@app.route('/resume/search', methods=['POST'])
@login_required
def search_resume():

    form = ResumeSearchForm()

    if not bool(form.ft_search.data):
        # return(RetCodes.missing_ent_attrs_error.value, "Search criteria not specified.".format(tenantID), None)
        return redirect(url_for('show_resume_browser_page'))

    (retCode, msg, resumeList) = resumeUtils.search_resumes(session.get('tenant_id'),
                                                            form.ft_search.data)

    if (retCode == resumeUtils.RetCodes.success.value):
        return render_template('resume/list.html', resumeList=resumeList, form=form)
    else:
        flash(retCode + ':' + msg, "is-danger")
        return render_template('resume/list.html', resumeList=None, form=form)


@app.route('/jd/searchNonShortlistedResumes', methods=['POST'])
@login_required
def search_non_shortlisted_resumes():

    form = ResumeSearchForm()

    _logger.debug('Job ID is %s & search criteria is %s',
                  form.job_id.data, form.ft_search.data)

    (retCode, msg, resumeList) = jdUtils.get_resumes_not_associated_with_job(form.job_id.data,
                                                                             form.ft_search.data, session.get('tenant_id'))
    #_logger.debug("ResumeList is %s", resumeList)
    if (retCode == jdUtils.RetCodes.success.value):
        # return render_template('resume/list.html', resumeList = resumeList, form = form )
        _logger.debug('ready to render')
        _logger.debug(
            'Non shortlisted resumes count found is %s', len(resumeList))
        # return render_template('/showHomepage')
        # return redirect(url_for("show_home_page"),303)

        return render_template('/jd/non_shortlisted_candidates_list.html',
                               resumeList=resumeList,
                               job_id=form.job_id.data,
                               searchForm=form)

    else:
        flash(retCode + ':' + msg, "is-danger")
        return render_template('jd/non_shortlisted_candidates_list.html', resumeList=resumeList, job_id=form.job_id.data, searchForm=form)


@app.route('/resume/showBrowser', methods=['GET'])
@login_required
def show_resume_browser_page():
    results = resumeUtils.list_resumes_by_tenant(session.get('tenant_id'))
    form = ResumeSearchForm()

    if (results[0] == resumeUtils.RetCodes.success.value):
        _logger.debug('success')
        resumeList = results[2]
        # for resume in resumeList:
        #	_logger.debug(resume.name)
        return render_template('resume/list.html', resumeList=resumeList, form=form)
    else:
        flash(results[0] + ':' + results[1], "is-danger")
        return render_template('resume/list.html', resumeList=None)


@app.route('/resume/showEditPage/<int:id>', methods=['GET'])
@login_required
def show_resume_edit_page(id):

    _logger.debug('inside edit resume page for  ID {0} '.format(id))

    #loggedInUserID = session.get('user_id')

    form = ResumeForm()
    form.id.data = id
    form.referrer.data = request.referrer

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
        flash(results[0] + ':' + results[1], "is-danger")
        return redirect(url_for("show_home_page"))


@app.route('/resume/download/<int:id>', methods=['GET'])
@login_required
def resume_download(id):

    try:
        (code, msg, resume) = resumeUtils.get(id)
        assert code == resumeUtils.RetCodes.success.value, "Failed to fetch resume {0} ".format(
            id)

        if resume.resume_content == None or resume.resume_filename == None:
            flash("No resume is attached with this candidate", "is-info")
            #_logger.debug("called from %s", request.referrer)
            # return redirect(url_for("show_resume_browser_page"))
            return redirect(request.referrer)
        else:
            file_data = bytes(resume.resume_content)

            f = open(resume.resume_filename, "wb")
            f.write(file_data)
            f.close()  # path = os.path.join(app.root_path + UPLOAD_FOLDER, filename)

            return send_file(resume.resume_filename, as_attachment=True)
            # return redirect(request.referrer)

    except Exception as e:
        flash(str(e), "is-danger")
        return redirect(request.referrer)


@app.route('/jd/download/<int:id>', methods=['GET'])
@login_required
def jd_download(id):
    #assert request.args['resume'], "Did not find resume key in request parameters."

    #filename = request.args['resume']
    try:
        (code, msg, jd) = jdUtils.get(id)
        assert code == jdUtils.RetCodes.success.value, "Failed to fetch job {0} ".format(
            id)

        if jd.client_jd == None or jd.jd_file_name == None:
            flash("No client JD is attached with this job", "is-info")
            return redirect(url_for("show_jd_all_page"))
        else:
            file_data = bytes(jd.client_jd)

            f = open(jd.jd_file_name, "wb")
            f.write(file_data)
            f.close()  # path = os.path.join(app.root_path + UPLOAD_FOLDER, filename)

            return send_file(jd.jd_file_name, as_attachment=True)

    except Exception as e:
        flash(str(e), "is-danger")
        return redirect(url_for("show_jd_all_page"))


'''
@app.route('/resume/showshortlistpage', methods = ['GET'])
@login_required
def show_resume_shortlist_page():

	try:
		_logger.debug('inside shortlist resume page for  ID {0} '.format(id))

		assert request.args.get('id'), "Resume ID request parameter not found."
		assert request.args.get('name'), "Candidate Name request parameter not found."

		form = ResumeShortlistForm()
		form.id.data = request.args.get('id')
		form.candidate_name.data = request.args.get('name')

		results = jdUtils.list_jds_by_tenant(session.get('tenant_id'))

		if (results[0] == jdUtils.RetCodes.success.value): 
			jdList = results[2]    
			for jd in jdList:
				_logger.debug(jd.title)
			form.selected_jd_list.choices = [(jd.id, jd.title + " | " + str(jd.id)) for jd in jdList]
			return render_template('resume/shortlist.html', form=form)		   
		else:
			flash (results[0] + ':' +results[1],"is-danger")
			return render_template('resume/shortlist.html',form = form)
	except Exception as e:
		flash (str(e),"is-danger")
		_logger.error("System Exeption occured. Details are %s", str(e),exc_info=1)
		return render_template('resume/shortlist.html',form = form)
'''


@app.route('/jd/showWorkPage/<int:id>', methods=['GET'])
@login_required
def show_shortlisted_candidates_page(id):

    _logger.debug('inside work on resumes page for JD ID {0} '.format(id))

    (retCode, msg, jd) = jdUtils.get(id)
    assert retCode == jdUtils.RetCodes.success.value, "Failed to fetch job details for id {0}. Error code is {1}. Error message is {2}".format(
        id, retCode, msg)

    (retCode, msg, appStatusCodesList) = resumeUtils.list_application_status_codes()
    assert retCode == resumeUtils.RetCodes.success.value, "Failed to fetch application status codes. Error code is {0}. Error message is {1}".format(
        retCode, msg)

    (retCode, msg, resumeList) = jdUtils.get_resumes_associated_with_job(id)
    assert retCode == jdUtils.RetCodes.success.value, "Failed to fetch resumes associated with job  id {0}. Error code is {1}. Error message is {2}".format(
        id, retCode, msg)

    searchForm = ResumeSearchForm()

    return render_template('jd/shortlisted_candidates_list.html', jd=jd,
                           resumeList=resumeList, actionTemplate="work",
                           appStatusCodesList=appStatusCodesList, searchForm=searchForm)

# This shows all the resumes / candidates not yet associated with a specific job id


@app.route('/jd/showShortlistPage/<int:job_id>', methods=['GET'])
@login_required
def show_shortlist_resumes_page(job_id):

    _logger.debug(
        'inside show shortlist resumes for Job ID {0} '.format(job_id))

    (retCode, msg, jd) = jdUtils.get(job_id)  # show JD summary on the page
    assert retCode == jdUtils.RetCodes.success.value, "Failed to fetch job details for id {0}. Error code is {1}. Error message is {2}".format(
        job_id, retCode, msg)

    # get all candidates not associated with a job
    (retCode, msg, resumeList) = jdUtils.get_resumes_not_associated_with_job(
        job_id, None, session.get('tenant_id'))
    assert retCode == jdUtils.RetCodes.success.value, "Failed to fetch resumes not associated with job  id {0}. Error code is {1}. Error message is {2}".format(
        job_id, retCode, msg)

    # get all candidates who are currently associated with the job
    (retCode, msg, shortlistedList) = jdUtils.get_resumes_associated_with_job(job_id)
    assert retCode == jdUtils.RetCodes.success.value, "Failed to fetch resumes associated with job  id {0}. Error code is {1}. Error message is {2}".format(
        job_id, retCode, msg)

    searchForm = ResumeSearchForm()
    searchForm.job_id.data = job_id
    # searchForm.source.data = "jd_shorlist_resumes_page"  #set the source field of search box

    return render_template('/jd/shortlist.html', jd=jd, job_id=jd.id,
                           resumeList=resumeList,
                           shortlistedList=shortlistedList, actionTemplate="shortlist",
                           searchForm=searchForm)


# @app.errorhandler(500)
def internal_error(error):
    _logger.error(str(error), exc_info=1)
    #flash (str(error),"is-danger")
    #flash("An unexpected error occured. Please contact you system administrator","is-danger")
    return render_template('utils/error.html'), 500

# Shortlists a resume for a Job.
# Expects query parameter jd_id, resume_id to be supplied.


@app.route('/jd/shortlist/', methods=['GET'])
@login_required
def jd_resume_shortlist():

    resume_id = request.args.get('resume_id')
    jd_id = request.args.get('job_id')

    (retCode, msg, data) = jdUtils.shortlist(resume_id, jd_id,
                                             datetime.now(
                                                 tz=timezone.utc), resumeUtils.ApplicationStatusCodes.shortlisted.value,
                                             session.get('user_id'))

    if retCode == jdUtils.RetCodes.success.value:
        flash('Candidate successfully shortlisted. Happy recruiting !!!', "is-success")
    else:
        flash('Candidate shortlisting failed. Error details are as under - ' +
              retCode + ':' + msg, "is-danger")

    # redirect and show all the resumes shortlisted for this job
    # return redirect(url_for('show_resume_work_page', id = jd_id))

    # /jd/showShortlistPage/<int:job_id>
    return redirect(url_for('show_shortlist_resumes_page', job_id=jd_id))

# TODO deprecate we may need to delete this function


@app.route('/resume/shortlist', methods=['POST'])
@login_required
def resume_shortlist():

    _logger.debug('inside resume shortlist.')

    form = ResumeShortlistForm()

    loggedInUserID = session.get('user_id')
    _logger.debug('Resume id is {0}'.format(form.id.data))
    _logger.debug('Selected JD List is {0}'.format(form.selected_jd_list.data))

    (retCode, msg, data) = jdUtils.shortlist(form.id.data, form.selected_jd_list.data,
                                             datetime.now(
                                                 tz=timezone.utc), resumeUtils.ApplicationStatusCodes.shortlisted.value,
                                             loggedInUserID)

    if retCode == jdUtils.RetCodes.success.value:
        flash(retCode + ':' + msg, "is-success")
        return redirect(url_for("show_resume_browser_page"))
        # return render_template('resume/shortlist.html', form= form)

    else:
        flash(retCode + ':' + msg, "is-danger")
        # form.submit.errors.append(results[1])
        return redirect(url_for("show_resume_browser_page"))
    # else:
    #	return render_template('resume/shortlist.html', form= form)


@app.route('/jd/showJobAppUpdatePage', methods=['GET'])
@login_required
def show_job_application_update_page():

    assert 'resume_id' in request.args, "Query parameter {0} not found in request".format(
        'resume_id')
    resume_id = request.args.get('resume_id')

    assert 'job_id' in request.args, "Query parameter {0} not found in request".format(
        'job_id')
    job_id = request.args.get('job_id')

    _logger.debug('inside show Job application update page for Job ID {0}, resume ID {1} '.format(
        job_id, resume_id))

    form = ApplicationStatusUpdate()
    form.resume_id.data = resume_id
    form.job_id.data = job_id
    form.change_date.data = datetime.now(tz=timezone.utc)

    (retCode, msg, jd) = jdUtils.get(job_id)  # show JD summary on the page
    assert retCode == jdUtils.RetCodes.success.value, "Failed to fetch job details for id {0}. Error code is {1}. Error message is {2}".format(
        job_id, retCode, msg)

    (retCode, msg, resume) = resumeUtils.get(resume_id)
    assert retCode == resumeUtils.RetCodes.success.value, "Failed to fetch resume associated with resume  id {0}. Error code is {1}. Error message is {2}".format(
        resume_id, retCode, msg)

    (retCode, msg, appStatusList) = resumeUtils.list_application_status_codes()
    assert retCode == resumeUtils.RetCodes.success.value, "Failed to get application status codes. Error code is {0} & error message is {1}".format(
        retCode, msg)

    form.new_status.choices = [
        (app_status.id, app_status.description) for app_status in appStatusList]

    return render_template('/jd/job_app_update.html', jd=jd, resume=resume,
                           statusList=appStatusList, form=form)


@app.route('/jd/updateJobApplicationStatus', methods=['POST'])
@login_required
def update_job_application_status():

    form = ApplicationStatusUpdate()

    # resume_id = form.resume_id.data #request.args.get('resume_id')
    # job_id = form.job_id.data #request.args.get('job_id')
    #new_status_code = form.new_status.data

    (retCode, msg, retData) = jdUtils.insert_job_application_status(form.job_id.data, form.resume_id.data,
                                                                    form.change_date.data, session.get(
                                                                        'user_id'),
                                                                    form.new_status.data, form.notes.data)

    if retCode == jdUtils.RetCodes.success.value:
        flash("Status updated successfully.", "is-success")

        file_loader = FileSystemLoader('./conf')
        env = Environment(loader=file_loader)
        template = env.get_template('job_appl_status_change.template')

        body = template.render(resumeID=str(form.resume_id.data), jobID=str(
            form.job_id.data), new_status=str(form.new_status.data))
        # send email
        emailUtils.sendMail_async(
            session["email_id"], 'Status change notification', body, 'plain')

        _logger.debug("Email sent successfully.")

    else:
        flash("Status update failed. Failure detail as follow - " +
              retCode + ':' + msg, "is-danger")

    return redirect(url_for('show_shortlisted_candidates_page', id=form.job_id.data))


@app.route('/jd/showSummaryPage/<int:job_id>', methods=['GET'])
@login_required
def show_job_summary_page(job_id):

    # get the job details to show the job header
    (retCode, msg, jd) = jdUtils.get(job_id)
    assert retCode == jdUtils.RetCodes.success.value, "Failed to fetch job details for job_id {0)".format(
        job_id)

    # get the summary
    (retCode, msg, jobStatusSummary) = jdUtils.get_job_status_summary(job_id)
    assert retCode == jdUtils.RetCodes.success.value, "Failed to fetch job status summary for job_id {0)".format(
        job_id)

    return render_template("jd/show_status_summary_page.html", jd=jd, statusSummary=jobStatusSummary)

# /reports/showClientWiseSummary


@app.route('/reports/showClientWiseSummary', methods=['GET'])
@login_required
def show_clientwise_summary_report_page():

    # get the summary
    (retCode, msg, clientSummary) = reports.get_client_wise_summary_report(
        session["tenant_id"])
    assert retCode == reports.RetCodes.success.value, "Failed to fetch client wise summary report"

    return render_template("reports/show_clientwise_summary_reportpage.html", clientSummary=clientSummary)


@app.route('/reports/showClientWiseJobApplicationStatusSummary', methods=['GET'])
@login_required
def show_clientwise_job_application_status_summary_report_page():

    (retCode, msg, clientSummary) = reports.get_client_wise_job_application_status_summary_report(
        session["tenant_id"])
    assert retCode == reports.RetCodes.success.value, "Failed to fetch client wise job application summary report"

    return render_template("reports/show_clientwise_job_app_summary_reportpage.html", clientSummary=clientSummary)


@app.route('/reports/showClientWiseRevenueOpportunitySummary', methods=['GET'])
@login_required
def show_clientwise_revenue_opportunity_summary_report_page():

    (retCode, msg, clientSummary) = reports.get_client_wise_revenue_opportunity_report(
        session["tenant_id"])
    assert retCode == reports.RetCodes.success.value, "Failed to fetch client wise job application summary report"

    return render_template("reports/show_clientwise_revenue_opportunity_reportpage.html", clientSummary=clientSummary)


@app.route('/user/showResetPassword', methods=['GET'])
@login_required
def show_reset_password():

    form = ResetPasswordForm()

    form.id.data = session["user_id"]
    form.email.data = session["email_id"]
    # flash("Password Reset Page","is-success")
    return render_template("user/password_reset.html", form=form)


@app.route('/user/doResetPassword', methods=['POST'])
@login_required
def do_reset_password():

    form = ResetPasswordForm()

    form.id.data = session["user_id"]
    form.email.data = session["email_id"]
    # print("Form Data : ", form.id.data,form.email.data,form.current_password.data,form.confirm.data,form.new_password.data)
    # userUtils.check_cur_pass_and_newPass(form.id.data,form.email.data,form.current_password.data,form.new_password.data)
    if((form.current_password.data == form.new_password.data)):
        flash('Current password and New password must be different', "is-danger")
        return redirect(url_for('show_reset_password'))

    elif((form.new_password.data == form.confirm.data)):
        (retCode, msg, data) = userUtils.do_reset_password(form.id.data,
                                                           form.email.data, form.current_password.data, form.new_password.data)
        if (retCode == userUtils.RetCodes.success.value):
            session.clear()
            # do_signout()
            flash(
                "Password reset successfully. Please sign-in again with your new password", "is-success")
            return redirect(url_for("show_signin_page"))
        else:
            flash("Password reset failed. {0} ".format(msg), "is-danger")
            return render_template("password_reset.html", form=form)

    else:
        # print("Password Not matched")
        # flash ("New Password and Confirm Password must be same", "is-danger")
        flash('New Password and Confirm new password must be same', "is-danger")
        return redirect(url_for('show_reset_password'))


@app.route('/user/forgotPassword', methods=['POST'])
def do_forgot_password():
    email = request.form.get('email')
    user = userUtils.get_user_by_email(email)
    if not user[2]:
        flash(
            'This email is not registerd with us, try again with a different email', "is-danger")
        return redirect(url_for('show_signin_page'))
    else:
        new_password = 'WeRecruit2022$'
        userUtils.do_forgot_password(
            user[2].id, user[2].email, user[2].password, new_password)
        emailSubject = 'Password Reset Successfully'
        emailBody = render_template('user/forgot_password.html')
        emailContentType = 'html'
        emailUtils.sendMail(user[2].email, subject=emailSubject,
                            body=emailBody, contentType=emailContentType)

        flash('A new password has been sent to your email successfully', "is-success")
        return redirect(url_for('show_signin_page'))


@app.route('/user/showManageUsersPage', methods=['GET'])
@login_required
def show_manage_users_page():

    #form = ResetPasswordForm()

    #form.id.data = session["user_id"]
    #form.email.data = session["email_id"]

    (retCode, msg, userList) = userUtils.list_users(session["tenant_id"])
    assert retCode == userUtils.RetCodes.success.value, msg

    return render_template("user/manage_users.html", userList=userList)


@app.route('/user/showAddPage', methods=['GET'])
@login_required
def show_add_user_page():

    form = UserForm()

    form.user_id.data = constants.NEW_ENTITY_ID
    form.role.choices = [(userUtils.RoleIDs.ADMIN.value, 'Admin'),
                         (userUtils.RoleIDs.RECRUITER.value, 'Recruiter')]

    return render_template("user/edit.html", form=form)


@app.route('/user/showEditPage/<int:id>', methods=['GET'])
@login_required
def show_edit_user_page(id):

    form = UserForm()

    (retcode, msg, user) = userUtils.get(id)
    if (retcode == userUtils.RetCodes.success.value):
        #flash (msg,"is-info")
        form.user_id.data = user.id
        form.name.data = user.name
        form.email.data = user.email
        form.password.data = user.password

        _logger.debug(('Role ID is : {0} ').format(str(user.rid)))

        form.role.choices = [(userUtils.RoleIDs.ADMIN.value, 'Admin'),
                             (userUtils.RoleIDs.RECRUITER.value, 'Recruiter')]
        form.role.data = user.rid

        return render_template("user/edit.html", form=form)
    else:
        flash(msg, "is-danger")
        return redirect(url_for("show_manage_users_page"))


@app.route('/user/showDeletePage/<int:id>', methods=['GET'])
@login_required
def show_delete_user_page(id):
    return render_template("user/delete.html", id=id)


@app.route('/user/delete/<int:id>', methods=['GET'])
@login_required
def do_delete_user(id):

    (retcode, msg, updated_rows) = userUtils.delete(id)

    if (retcode == userUtils.RetCodes.success.value):
        _logger.debug(
            'User delete successful. Rows updated is '.format(updated_rows))
        flash(msg, "is-success")
    else:
        _logger.debug(
            'User delete failed. Rows updated is '.format(updated_rows))
        flash(msg, "is-danger")
        # return redirect(url_for("show_manage_users_page"))
    return redirect(url_for("show_manage_users_page"))


@app.route('/user/save', methods=['POST'])
@login_required
def save_user():

    form = UserForm()

    (retcode, msg, data) = userUtils.save_user(session['tenant_id'],
                                               form.user_id.data, form.name.data, form.email.data,
                                               form.password.data, form.role.data)

    if retcode == userUtils.RetCodes.success.value:
        flash(msg, "is-info")
        return redirect(url_for("show_manage_users_page"))
    else:
        flash(msg, "is-danger")
        return render_template("user/edit.html", form=form)


def get_file_handler():
    file_handler = TimedRotatingFileHandler(
        constants.LOG_FILENAME_WEB, when='midnight')
    file_handler.setFormatter(logging.Formatter(constants.LOG_FORMAT))
    file_handler.setLevel(int(os.environ.get("LOG_LEVEL", 20)))
    return file_handler


if __name__ == "__main__":

    # load_dotenv()
    # load_dotenv(find_dotenv())
    #app.secret_key = os.environ.get("FLASK_SESSION_API_KEY")
    # logging.basicConfig(filename = constants.LOG_FILENAME_WEB, format=constants.LOG_FORMAT,
    #				level=int(os.environ.get("LOG_LEVEL",20)))

    # _logger.addHandler(get_file_handler())
    print("Effective logging level is :", _logger.getEffectiveLevel())

    app.run(debug=True)
