from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField, HiddenField
from wtforms.fields.core import IntegerField
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

class JDCreateForm(FlaskForm):
    
    title = StringField('Title', validators=[DataRequired(message='Enter Title')])
    details = TextAreaField('Details', validators=[DataRequired('Enter  Details')])

    client = StringField('Client Name', validators=[DataRequired('Enter Client Name')])
    hiring_mgr_name = StringField('Hiring Manager Name', validators=[DataRequired('Enter hiring manager Name')])
    hiring_mgr_email = StringField('Hiring Manager Email', validators=[DataRequired('Enter hiring manager Email')])

    total_positions = StringField('Total Positions', validators=[DataRequired('Enter number of positions')])

    submit = SubmitField('Save JD')

class JDHeaderForm( FlaskForm):
    id = HiddenField('ID' )
    
    title = StringField('Title', validators=[DataRequired(message='Enter Title')])
    details = TextAreaField('Details', validators=[DataRequired('Enter  Details')])

    client = StringField('Client Name', validators=[DataRequired('Enter Client Name')])
    total_positions = IntegerField('Total Positions', validators=[DataRequired('Enter number of positions')])

    submit = SubmitField('Save')

