from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email

class SignUpForm(FlaskForm):

    company_name = StringField('Company Name', validators=[DataRequired(message='Please enter company name')])
    
    name = StringField('User Name', validators=[DataRequired(message='Please enter your name')])
    email = StringField('Email', validators=[DataRequired(message='Please enter email ID'),Email(message='Please enter a valid email address')])
    password = PasswordField('Password', validators=[DataRequired('Please enter password.')])
    
    submit = SubmitField('Create WeRecruit account')

class SignInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message='Please enter email ID'),Email(message='Please enter a valid email address')])
    password = PasswordField('Password', validators=[DataRequired('Please enter password.')])
    
    submit = SubmitField('Sign In')


