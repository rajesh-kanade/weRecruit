from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectMultipleField, SelectField, StringField, PasswordField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email,NumberRange
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import IntegerField, DateField

import jdUtils


class SignUpForm(FlaskForm):

    company_name = StringField('Company Name', validators=[DataRequired(message='Please enter company name')])
    
    name = StringField( 'Admin User Name', validators=[DataRequired(message='Please enter your name')])
    email = StringField('Admin Email', validators=[DataRequired(message='Please enter email ID'),Email(message='Please enter a valid email address')])
    password = PasswordField('Password', validators=[DataRequired('Please enter password.')])
    
    submit = SubmitField('Create WeRecruit account')

class SignInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message='Please enter email ID'),Email(message='Please enter a valid email address')])
    password = PasswordField('Password', validators=[DataRequired('Please enter password.')])
    
    submit = SubmitField('Sign In')

class ResetPasswordForm(FlaskForm):

    id = HiddenField('ID' )

    email = StringField('Email', validators=[DataRequired(message='Please enter email ID'),Email(message='Please enter a valid email address')])
    current_password = PasswordField('Current Password', validators=[DataRequired('Please enter current password.')])
    new_password = PasswordField('New Password', validators=[DataRequired('Please enter new password.')])

    submit = SubmitField('Save')

class UserForm(FlaskForm):

    #company_name = StringField('Company Name', validators=[DataRequired(message='Please enter company name')])
    user_id = HiddenField('ID' )
    
    name = StringField( 'Name', validators=[DataRequired(message='Please enter your name')])
    email = StringField('Email', validators=[DataRequired(message='Please enter email ID'),Email(message='Please enter a valid email address')])
    password = PasswordField('Password', validators=[DataRequired('Please enter password.')])

    #role = SelectField('Role', choices=[(int(userUtils.RoleIDs.ADMIN.value), 'Admin'), 
    #                    (int(userUtils.RoleIDs.RECRUITER.value), 'Recruiter')])
    
    role = SelectField('Select Role', coerce=int)
    
    submit = SubmitField('Save')

class JDForm(FlaskForm):
    
    id = HiddenField('ID' )

    title = StringField('Title*', validators=[DataRequired(message='Enter Title*')])
    details = TextAreaField('Details')
    total_positions = IntegerField('Total Positions', 
                        validators=[DataRequired('Enter number of positions'),NumberRange(min=1, max=5)])
                   
    open_date = DateField('Open Date',validators=[DataRequired('Enter  Open Date')])

    client = StringField('Client Name*', validators=[DataRequired('Enter Client Name')])
    client_jd = FileField('Client JD File')

    location = StringField('Location')
    yrs_of_exp = DecimalField("Years of Experience")
    primary_skills = TextAreaField('Primary Skills')
    secondary_skills = TextAreaField('Secondary Skills')
    ctc_min = DecimalField("CTC Min Range")
    ctc_max = DecimalField("CTC Max Range")
    ctc_currency = SelectField( "Currency", choices =[('INR', 'INR'),('USD', 'USD')])
    fees_percent = DecimalField("Fees Percent")
    warranty_in_months = IntegerField("Warranty in months")

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
    
    id = HiddenField('Resume ID')
    
    candidate_resume = FileField('Resume')

    candidate_name = StringField('Candidate Name*',validators=[DataRequired(message='Candidate Name can not be blank.')])
    candidate_email = StringField('Candidate Email*',validators=[DataRequired(message='Candidate Email can not be blank.')])
    candidate_phone = StringField('Candidate Phone*',validators=[DataRequired(message='Candidate Phone can not be blank.')])

    submit = SubmitField('Save')

class ResumeSearchForm( FlaskForm):
        
    #ft_search = StringField('',validators=[DataRequired(message='Search field can not be empty.')])
    ft_search = StringField('Enter search criteria.')
    #source = StringField('source')
    job_id = HiddenField()
    submit = SubmitField('Search')

class ResumeShortlistForm ( FlaskForm):
    id = HiddenField('Resume ID') #IntegerField('resume_ID',render_kw={'readonly': True})
    candidate_name = StringField('Candidate Name',validators=[DataRequired(message='Candidate Name can not be blank.')])
    selected_jd_list = SelectMultipleField('Existing JDs')

    submit = SubmitField('shortlist')

class ApplicationStatusUpdate( FlaskForm):
    job_id = HiddenField()
    resume_id = HiddenField()
    current_status_id = HiddenField()
    current_status_desc = StringField('Current Status',render_kw={'readonly': True})

    new_status = SelectField('Select New Status')
    notes = TextAreaField('Notes')
    change_date = DateField('Update Date & Time', format='%Y-%m-%d')
    submit = SubmitField('Update')
