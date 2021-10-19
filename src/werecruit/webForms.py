from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, BooleanField, SubmitField,TextAreaField, HiddenField
from wtforms.fields.core import IntegerField,DateField
from wtforms.validators import DataRequired, Email,NumberRange
from flask_wtf.file import FileField, FileRequired, FileAllowed


import jdUtils

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
    total_positions = IntegerField('Total Positions', 
                        validators=[DataRequired('Enter number of positions'),NumberRange(min=1, max=5)])
                   
    open_date = DateField('Open Date',validators=[DataRequired('Enter  Open Date')])

    client = StringField('Client Name', validators=[DataRequired('Enter Client Name')])
    status = SelectField('Status', choices=[(jdUtils.JDStatusCodes.open.value, 'Open'), 
                        (jdUtils.JDStatusCodes.draft.value, 'Draft'), 
                        (jdUtils.JDStatusCodes.close.value, 'Close')])


    hr_name = StringField('HR Name')
    hr_email = StringField('HR Email')
    hr_phone = StringField('HR Phone')

    intv_panel_name_1 = StringField('Name')
    intv_panel_email_1 = StringField('Email')
    intv_panel_phone_1 = StringField('Phone')

    intv_panel_name_2 = StringField('Name')
    intv_panel_email_2 = StringField('Email')
    intv_panel_phone_2 = StringField('Phone')

    hiring_mgr_name = StringField('Hiring Manager Name')
    hiring_mgr_email = StringField('Hiring Manager Email')
    hiring_mgr_phone = StringField('Hiring Manager Phone')

    
    submit = SubmitField('Save JD')

class JDHeaderForm( FlaskForm):
    
    id = HiddenField('ID' )
    
    title = StringField('Title', validators=[DataRequired(message='Enter Title')])
    details = TextAreaField('Details', validators=[DataRequired('Enter  Details')])

    client = StringField('Client Name', validators=[DataRequired('Enter Client Name')])
    total_positions = IntegerField('Total Positions', validators=[DataRequired('Enter number of positions')])

    submit = SubmitField('Save')

class JDApply( FlaskForm):
    
    jd_id = IntegerField('Job Description ID',render_kw={'readonly': True} )
    jd_title = StringField('Job Title',render_kw={'readonly': True})

    resume_id = IntegerField('resume_ID',render_kw={'readonly': True})
    
    candidate_resume = FileField('Resume', validators=[FileRequired(), FileAllowed(['pdf', 'docx'], 'Word and PDF files only!')])
    candidate_name = StringField('Candidate Name')
    candidate_email = StringField('Candidate Email')
    candidate_phone = StringField('Candidate Phone')

    submit = SubmitField('Apply')

class ResumeForm( FlaskForm):
    
    id = HiddenField('Resume ID') #IntegerField('resume_ID',render_kw={'readonly': True})
    
    candidate_resume = FileField('Resume', validators=[FileRequired(), FileAllowed(['pdf', 'docx'], 'Unsupported file type. Upload only Word or PDF files!')])
    candidate_name = StringField('Candidate Name',validators=[DataRequired(message='Candidate Name can not be blank.')])
    candidate_email = StringField('Candidate Email')
    candidate_phone = StringField('Candidate Phone')

    submit = SubmitField('Upload Resume')



