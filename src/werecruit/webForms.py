from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField, HiddenField
from wtforms.fields.core import IntegerField,DateField
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

class JDForm(FlaskForm):
    
    id = HiddenField('ID' )

    title = StringField('Title', validators=[DataRequired(message='Enter Title*')])
    details = TextAreaField('Details', validators=[DataRequired('Enter  Details')])
    total_positions = IntegerField('Total Positions', validators=[DataRequired('Enter number of positions')])
    open_date = DateField('Open Date',validators=[DataRequired('Enter  Open Date')])

    client = StringField('Client Name', validators=[DataRequired('Enter Client Name')])

    hiring_mgr_name = StringField('Hiring Manager Name', validators=[DataRequired('Enter hiring manager Name')])
    hiring_mgr_email = StringField('Hiring Manager Email', validators=[DataRequired('Enter hiring manager Email')])
    hiring_mgr_phone = StringField('Hiring Manager Phone')

    intv_panel_name_1 = StringField('Name')
    intv_panel_email_1 = StringField('Email')
    intv_panel_phone_1 = StringField('Phone')

    intv_panel_name_2 = StringField('Name')
    intv_panel_email_2 = StringField('Email')
    intv_panel_phone_2 = StringField('Phone')


    submit = SubmitField('Save JD')

class JDHeaderForm( FlaskForm):
    id = HiddenField('ID' )
    
    title = StringField('Title', validators=[DataRequired(message='Enter Title')])
    details = TextAreaField('Details', validators=[DataRequired('Enter  Details')])

    client = StringField('Client Name', validators=[DataRequired('Enter Client Name')])
    total_positions = IntegerField('Total Positions', validators=[DataRequired('Enter number of positions')])

    submit = SubmitField('Save')

