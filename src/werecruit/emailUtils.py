
import os
import constants
import smtplib

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
#logging.propagate = False 
from dotenv import load_dotenv , find_dotenv
load_dotenv(find_dotenv())
#logging.basicConfig(format=constants.LOG_FORMAT, level=int(os.environ.get("LOG_LEVEL",20)))
_logger = logging.getLogger()


def readEmails():
	mailbox = None 
	try:
		_logger.info("Reading mailbox")
		
		mailserver = os.environ.get("IMAP_MAIL_SERVER")
		email = os.environ.get("IMAP_MAILBOX")
		password = os.environ.get("IMAP_MAILBOX_PWD")
		folder = os.environ.get("IMAP_FOLDER")

		_logger.info( "Reading email configurations")
		_logger.info("Mail server is {0} ".format(mailserver))
		_logger.info(email)
		#logging.debug(password)
		_logger.info(folder)

		mailbox = MailBox(mailserver)

		mailbox.login(email, password, initial_folder=folder)  

		_logger.info("Logged into mail box")

		_logger.info("start reading emails")
		
		for msg in mailbox.fetch(AND( seen = False )):  #should be False in prod
			try:	
				_logger.debug(msg.subject)
				_logger.debug(msg.text)
				_logger.debug(msg.from_)
				
				from_email_addr =str(msg.from_) #is this really required?
				_logger.debug('Email received from {0}'.format(from_email_addr))

				#check if the from address is registered user. 
				#if he is not then send email and continue to next message
				(retcode,retMsg,user) = userUtils.get_user_by_email(msg.from_)
				if retcode != userUtils.RetCodes.success.value:
					_logger.warning("Failed to get user record associated with email ID")
					sendMail(from_email_addr,'Resume upload failure notification','Your email ID is not registered with weRecruit.','plain')
					continue
				
				#Now go thru attachment and for each attachment create a resume record in our system.
				for att in msg.attachments:
					try:
						#_logger.debug(os.getcwd(),att.filename, att.content_type)

						#cwd = os.getcwd() + "\\";
						#_logger.debug("working dir is " + cwd)

						#TODO check for supported file type and exit if unsupported

						#save the attachment in temp file
						file_name = "./src/werecruit/temp/" + att.filename
						f = open(file_name,'wb' )
						f.write( att.payload)
						f.close()
						
						candidate_name ='Waiting for Resume parser to update.'
						candidate_email ='Waiting for Resume parser to update.'
						candidate_phone ='Waiting for Resume parser to update.'

						(retcode,msg,resumeId) = resumeUtils.save_resume(constants.NEW_ENTITY_ID, file_name,
													candidate_name,candidate_email,candidate_phone,user.id)
										
						if file_name is not None and os.path.exists(file_name):
							os.remove(file_name)								


						# Save resume has failed so send email , log error and continue to next attachment
						if retcode != resumeUtils.RetCodes.success.value:
							_logger.warning("Failed to save file {0} as resume".format(file_name))
							sendMail(from_email_addr,'Resume upload failure notification',"Failed to save file {0} as resume".format(file_name),'plain')
							continue
						
						# Send success resume save email
						file_loader = FileSystemLoader('./conf')
						env = Environment(loader=file_loader)
						template = env.get_template('resume_upload_response.template')		
						body = template.render(resumeID = resumeId )
						sendMail(from_email_addr,'Resume upload notification',body,'plain')

					except Exception as att_e:
						#error occured while processing an attachment in a message 
						# so log error and continue
						_logger.error(att_e)
						sendMail(from_email_addr,'Resume upload failure notification',str(att_e),'plain')
						continue
			
			except Exception as msg_e:
				#error occured while processing email message, 
				# log error & continue
				_logger.error(msg_e)
				sendMail(from_email_addr,'Resume upload failure notification',str(msg_e),'plain')
				continue

	except Exception as e:
		_logger.error( e )
		#mailbox.logout()

	finally:
		if mailbox is not None:
			mailbox.logout()
			_logger.info("successfully logged out from mailbox")


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

	#sendMail('rrkanade22@yahoo.com', "test subject", "test body",'plain')
	#time.sleep(60)
	
	#while True:
	logging.basicConfig(level=logging.DEBUG)
	readEmails()
	#	time.sleep(60)

