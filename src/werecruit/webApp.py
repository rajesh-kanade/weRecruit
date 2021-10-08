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
from webForms import JDCreateForm, SignUpForm , SignInForm

import logging
import userUtils
import functools

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    return render_template('index.html')        
        

@app.route('/user/showSigninPage')
def show_signin_page():
    form = SignInForm()
    return render_template('sign_in.html', form = form)

@app.route('/user/doSignout', methods = ['GET'])
def do_signout():

    if 'user_id' in session :
        session.pop('user_id', None)
        flash('Successfully logged out.',"is-info")
        return redirect('/user/showSigninPage')    

@app.route('/user/doSignin', methods = ['POST'])
def do_signin():

    form = SignInForm()

    results = userUtils.do_SignIn( form.email.data, form.password.data)

    if (results[0] == userUtils.RetCodes.success.value):        
        flash (results[1],"is-info")
        user = results[2] 

        session["user_id"] = user.id  #form.email.data
        session["user_name"] = user.name #'Mr. Customer'

        return render_template('home.html')
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
        return render_template('sign_in.html', form = SignInForm())
    else:
        flash (results[0] + ':' +results[1],"is-danger")
        return render_template('sign_up.html', form=form)

def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "user_id" not in session:
            flash ( "You are not authenticated. Please login to access this page.","is-danger")
            return redirect(url_for("show_signin_page"))

        return func(*args, **kwargs)

    return secure_function

@app.route('/jd/showCreatePage')
@login_required
def show_jd_create_page():

    form=JDCreateForm()
    return render_template('create_jd.html', form = form)


if __name__ == "__main__":
    app.run()