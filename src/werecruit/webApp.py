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
from webForms import SignUpForm , SignInForm

import logging
import userUtils

class User:
    
    def __init__(self, name, email):
        self.name = name
        self.email = email
        

    #def __repr__(self):
    #    return f'<User: {self.username}>'

users = []



app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    return render_template('index.html')        
        
'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        
        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('profile'))

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile.html')
'''

@app.route('/user/showSigninPage')
def show_signin_page():
    form = SignInForm()
    return render_template('sign_in.html', form = form)

@app.route('/user/doSignin', methods = ['POST'])
def do_signin():

    form = SignUpForm()

    results = userUtils.do_SignIn( form.email.data, form.password.data)

    if (results[0] == userUtils.RetCodes.success.value):        
        flash (results[1],"is-info")
        session["user_id"] = form.email.data
        session["user_name"] = 'Mr. Customer'
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

    userAttrs['id'] = form.email.data
    userAttrs['password'] = form.password.data
    userAttrs['name'] = form.name.data
    userAttrs['status'] =userUtils.Status.active.value

    results = userUtils.create_user( userAttrs)

    if (results[0] == userUtils.RetCodes.success.value):        
        flash ("Congratulations!!! '{0}' successfully signed up. Get started by signing in now.".format(form.name.data), "is-info")
        #form.success = True
        return render_template('sign_in.html', form = SignInForm())
    else:
        #return jsonify({RET_CODE: results[0],RET_MSG: results[1]}),400
        #error = results[1]
        #form.success = False
        flash (results[0] + ':' +results[1],"is-danger")
        return render_template('sign_up.html', form=form)



def render_otp():

    return render_template('otp.html')        


    

@app.route('/Sign in', methods = ['GET', 'POST'])
def sign_in():

    app.logger.info("hello_1")
    print("hello_1")

    render_Sign_in()

    print("rendered sign in")
    
    email = ''
    otp = ''

    print("variable initialization done")

    if request.method == 'POST':

        email = request.form['email']
        otp = request.form['otp']
        app.logger.info(email)
        app.logger.info(type(email))
        app.logger.info(otp)
        app.logger.info(type(otp))
        
    
    if(otp!="" and email!=""):
        
        ans = userUtils.userSignIn(email, otp)
        print(ans)
        if(ans == 0):
            print("Login Successful")
            #flash("Login Successful")
            return render_template('home.html')

        elif(ans == -1):
            print("Login Failed")
            flash("Login Failed")
            return render_template('Sign_in.html')

        elif(ans == -2):
            flash("Login failed with exception")
            print("Login failed with exception")
            return render_template('Sign_in.html')

        #users.append(User(name=name, surname=surname, email=email)
        #flash("Sign up successful")  
        #app.logger.info(users[-1].name)
        #app.logger.info(users[-1].surname)
        #app.logger.info(users[-1].email)
         
        return render_template('home.html')
    
    else:

        #return callotpGenMethod(email)

        #otp = ""
        #email = ""
 
        flash("All fields are to be filled")    
        return render_template('Sign_in.html')
    
@app.route('/otpGeneration', methods = ['POST']) 
def callotpGenMethod():

    #app.logger.info("generating otp...")

    print("otp gen")

    #render_otp()

    #print(flag)

    email = ''

    print("heyyy")

    if request.method == 'POST':

        email = request.form['email']
        
        app.logger.info(email)
        print(email)
        app.logger.info(type(email))
        print(type(email))
        
    
    if(email!=""):

        (ans,msg) = userUtils.getOTP(email)
        print(ans)
        app.logger.info(ans)

        if(ans == 0):

            #global flag

            print("returning to sign in page")
            
            #print(flag)
            #flash("Once you get the otp proceed further")
            #render_template('Sign_up.html', messages=['email':''])
            return redirect('/Sign in')
            #return render_template('otp.html')

        elif(ans == -1):

            flash("Email address provided is not registered with us.")

            return render_template('otp.html')       
    

        elif(ans == -2):

            print("in else flag is " + str(flag))
            
            print("else")
            
            flash("otp generation failed. Please try again.")
            
            #flash("Once you get the otp proceed further")
                 
            return render_template('otp.html')       

    else:

        #global flag

        #email = ""

        print("flag in final else " + str(flag))

        print("else")

        flash("Email cannot be blank.")
        
        return render_template('otp.html')    


@app.route('/showotpGenerationpage', methods = ['GET']) 
def callshowotpGenerationpage():

    print(" show otp gen")

    return render_otp()

    #render_template('otp.html')        


if __name__ == "__main__":
    app.run()