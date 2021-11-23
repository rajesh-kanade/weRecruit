import imaplib
import poplib
import os
import constants
import smtplib

#from userUtils import getUserConfig, get
#import resumeUtils

from imap_tools import MailBox, AND
import userUtils 
import resumeUtils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

from jinja2 import Environment, FileSystemLoader

import _thread
import time
import logging
_logger = logging.getLogger('emailUtils')

def readEmails():
	mailbox = None 
	try:
		_logger.info("Reading mailbox")
		
		mailserver = os.environ.get("IMAP_MAIL_SERVER")
		email = os.environ.get("IMAP_MAILBOX")
		password = os.environ.get("IMAP_MAILBOX_PWD")
		folder = os.environ.get("IMAP_FOLDER")

		_logger.info( "Reading email configurations")
		_logger.info("Mail server is ",mailserver)
		_logger.info(email)
		#logging.debug(password)
		_logger.info(folder)

		mailbox = MailBox(mailserver)

		mailbox.login(email, password, initial_folder=folder)  

		_logger.info("Logged into mail box")

		_logger.info("start reading emails")
		
		for msg in mailbox.fetch(AND( seen = True )):  #should be False in prod
			_logger.info(msg.subject)
			_logger.info(msg.text)
			for att in msg.attachments:
				_logger.debug(os.getcwd(),att.filename, att.content_type)
				cwd = os.getcwd() + "\\";
				_logger.debug("working dir is " + cwd)
				
				f = open("./src/werecruit/resume_uploads/" + att.filename,'wb' )
				f.write( att.payload)
				f.close()
				
				(candidate_name,candidate_email,candidate_phone) = resumeUtils.process_single_resume("./src/werecruit/resume_uploads/" + att.filename)
				_logger.debug(candidate_name)
				_logger.debug(candidate_email)
				_logger.debug(candidate_phone)
				
				if not bool(candidate_name):
					candidate_name ='Please change manually'

				if not bool(candidate_email):
					candidate_email ='Please change manually'

				if not bool(candidate_phone):
					candidate_name ='Please change manually'


				#TODO : instead of hardcoded recruiter id, we need to get recruiterID from email
				(retcode,msg,resumeId) = resumeUtils.save_resume(constants.NEW_ENTITY_ID, att.filename,candidate_name,
								candidate_email,candidate_phone,1)

				assert retcode == resumeUtils.RetCodes.success.value, "Failed to save resume sent via email. Please contact your sys admin."
				
				file_loader = FileSystemLoader('./conf')
				env = Environment(loader=file_loader)
				template = env.get_template('resume_upload_response.template')
		
				body = template.render(resumeID = resumeId )
				
				sendMail(email,'Resume upload notification',body,'plain')
		#mailbox.logout()
		_logger.info("logged out from mailbox")
	
	except Exception as e:
		_logger.error( e )
		#mailbox.logout()

	finally:
		if mailbox is not None:
			mailbox.logout()

	#res_dir_path = "./data/"
	#resume_List =  os.listdir(path=res_dir_path)

	#logging.debug("Start processing resumes from folder " + res_dir_path)

	'''for resume_file in resume_List:
		resumeUtils.process_single_resume(userID, str( res_dir_path + resume_file))
		os.remove(str( res_dir_path + resume_file))
	'''

def sendMail_async(ToEmailAddr, subject, body, contentType):
	_thread.start_new_thread ( sendMail,(ToEmailAddr, subject, body, contentType) )


def sendMail(ToEmailAddr, subject, body, contentType):
	
	ToEmailAddr = 'rkanade@gmail.com' #ToEmailAddr -> done purposefully to avoid sending emails to
	
	logging.info("Setting up SMTP server again")

	msg = MIMEMultipart()
	msg['From'] = os.environ.get("SMTP_MAIL_USERNAME")
	msg['To'] = ToEmailAddr
	msg['Subject'] = str(subject)

	msg.attach(MIMEText(body,contentType)) #'plain'

	_logger.debug( msg.as_string() )

	with smtplib.SMTP(os.environ.get("SMTP_MAIL_SERVER"), os.environ.get("SMTP_MAIL_PORT")) as server:
		server.login(os.environ.get("SMTP_MAIL_USERNAME"), os.environ.get("SMTP_MAIL_PASSWORD"))
		server.sendmail(os.environ.get("SMTP_MAIL_USERNAME"), ToEmailAddr, msg.as_string())
		server.close()

	_logger.info("Mail sent successfully.")


if __name__ == "__main__":
	#processEmailsForApp(constants.APP_CODE_CAMI);
	#processEmails("rrkanade22@yahoo.com","CAMI")
	logging.basicConfig(level=logging.DEBUG)

	#sendMail('rrkanade22@yahoo.com', "test subject", "test body",'plain')
	#time.sleep(60)
	
	#while True:
	readEmails()
	#	time.sleep(60)

