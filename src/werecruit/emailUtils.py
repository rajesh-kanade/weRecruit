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

def readEmails():

	try:
		print("Reading mailbox")

		#mailbox = MailBox('mail.fulgorithm.com')
		#(retCode,retMsg,mailserver) = userUtils.getUserConfig(userID,appID, "email_server")
		#(retCode,retMsg,email) = userUtils.getUserConfig(userID,appID, "mailbox")
		#(retCode,retMsg,password) = userUtils.getUserConfig(userID,appID, "password")
		#(retCode,retMsg,folder) = userUtils.getUserConfig(userID,appID, "folder")
		
		mailserver = os.environ.get("IMAP_MAIL_SERVER")
		email = os.environ.get("IMAP_MAILBOX")
		password = os.environ.get("IMAP_MAILBOX_PWD")
		folder = os.environ.get("IMAP_FOLDER")

		print( "printing email configurations")
		print("Mail server is ",mailserver)
		print(email)
		print(password)
		print(folder)

		mailbox = MailBox(mailserver)

		mailbox.login(email, password, initial_folder=folder)  

		print("Logged into mail box")

		print("start reading emails")

		for msg in mailbox.fetch(AND( seen = True )):  #shold be False
			print(msg.subject)
			print(msg.text)
			for att in msg.attachments:
				print(os.getcwd(),att.filename, att.content_type)
				cwd = os.getcwd() + "\\";
				print("working dir is " + cwd)
				
				f = open("./src/werecruit/resume_uploads/" + att.filename,'wb' )
				f.write( att.payload)
				f.close()
				
				resumeUtils.save_resume(constants.NEW_ENTITY_ID, att.filename,'Dummy Name',
								'Dummy Email','Dummy phone',1)
		
		mailbox.logout()
		print("logged out from mailbox")
	
	except Exception as e:
		print( e )
		print ( " Exception reading email ")

	#res_dir_path = "./data/"
	#resume_List =  os.listdir(path=res_dir_path)

	#print("Start processing resumes from folder " + res_dir_path)

	'''for resume_file in resume_List:
		resumeUtils.process_single_resume(userID, str( res_dir_path + resume_file))
		os.remove(str( res_dir_path + resume_file))
	'''

def sendMail(ToEmailAddr, subject, body, contentType):
	
	ToEmailAddr = 'rkanade@gmail.com' #ToEmailAddr -> done purposefully to avoid sending emails to
	
	print("Setting up SMTP server again")

	msg = MIMEMultipart()
	msg['From'] = os.environ.get("SMTP_MAIL_USERNAME")
	msg['To'] = ToEmailAddr
	msg['Subject'] = str(subject)

	msg.attach(MIMEText(body,contentType)) #'plain'

	print( msg.as_string() )

	with smtplib.SMTP(os.environ.get("SMTP_MAIL_SERVER"), os.environ.get("SMTP_MAIL_PORT")) as server:
		server.login(os.environ.get("SMTP_MAIL_USERNAME"), os.environ.get("SMTP_MAIL_PASSWORD"))
		server.sendmail(os.environ.get("SMTP_MAIL_USERNAME"), ToEmailAddr, msg.as_string())
		server.close()

	print("Mail sent successfully.")


if __name__ == "__main__":
	#processEmailsForApp(constants.APP_CODE_CAMI);
	#processEmails("rrkanade22@yahoo.com","CAMI")
	#sendMail('rrkanade22@yahoo.com', "test subject", "test body",'plain')
	readEmails()
