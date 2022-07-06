
from multiprocessing.sharedctypes import Value
import os
import constants
import smtplib

from imap_tools import MailBox, AND
import userUtils 
import resumeUtils
import jdUtils

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup

import _thread
import time
import re
import magic
import requests
import tempfile

import logging

from datetime import datetime
from datetime import timezone

#logging.propagate = False 
from dotenv import load_dotenv , find_dotenv
load_dotenv(find_dotenv())
#logging.basicConfig(format=constants.LOG_FORMAT, level=int(os.environ.get("LOG_LEVEL",20)))
_logger = logging.getLogger()

def process_single_file(file_name,userID):
	(resume_attr_list) = resumeUtils.process_single_resume(file_name)
	if bool(resume_attr_list['name']):
		candidate_name = resume_attr_list['name'][0]
	else:
		candidate_name = 'Resume parser can not update this field.Manual update required.'

	if bool(resume_attr_list['phone']):
		candidate_phone = resume_attr_list['phone'][0]
	else:
		candidate_phone = 'Resume parser can not update this field.Manual update required.'

	if bool(resume_attr_list['email']):
		candidate_email = resume_attr_list['email'][0]
	else:
		candidate_email = 'Resume parser can not update this field.Manual update required.'


	(retcode,retmsg,resumeId) = resumeUtils.save_resume(constants.NEW_ENTITY_ID, file_name,
								candidate_name,candidate_email,candidate_phone,userID)
					
	if file_name is not None and os.path.exists(file_name):
		os.remove(file_name)								

	return (retcode,retmsg,resumeId)



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
			msg.seen = True

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
				
				# Download links and save as attachment. This is how resumes are received from LinkedIN
				# if exceptions occur , log & move forward 
				try:
					downloadResumeFromLink(msg.subject, msg.html, from_email_addr,user.id)
				except Exception as drException1:
					_logger.error(drException1)

				#Now go thru attachment and for each attachment create a resume record in our system.
				for att in msg.attachments:
					try:
						file_name = constants.getUploadFolderPath() + att.filename

						f = open(file_name,'wb' )
						f.write( att.payload)
						f.close()
						
						(resume_attr_list) = resumeUtils.process_single_resume(file_name)
						if bool(resume_attr_list['name']):
							candidate_name = resume_attr_list['name'][0]
						else:
							candidate_name = 'Resume parser can not update this field.Manual update required.'
		
						if bool(resume_attr_list['phone']):
							candidate_phone = resume_attr_list['phone'][0]
						else:
							candidate_phone = 'Resume parser can not update this field.Manual update required.'

						if bool(resume_attr_list['email']):
							candidate_email = resume_attr_list['email'][0]
						else:
							candidate_email = 'Resume parser can not update this field.Manual update required.'


						(retcode,retmsg,resumeId) = resumeUtils.save_resume(constants.NEW_ENTITY_ID, file_name,
													candidate_name,candidate_email,candidate_phone,user.id)
										
						if file_name is not None and os.path.exists(file_name):
							os.remove(file_name)								


						# Save resume has failed so send email , log error and continue to next attachment
						if retcode != resumeUtils.RetCodes.success.value:
							_logger.warning("Failed to save file {0} as resume".format(file_name))
							sendMail(from_email_addr,'Resume upload failure notification',"Failed to save file {0} as resume".format(file_name),'plain')
							continue
						
						# see if jobID is mentioned in subject and if yes auto shortlist
						jobID = extractJobIdFromSubject( msg.subject)
						shortlistDownloadedResumes(jobID,resumeId,user.id)


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
			try:
				mailbox.logout()
				_logger.info("successfully logged out from mailbox")
			except Exception as e1:
				_logger.error("Exception occured while logging out of mailbox.",exc_info=1)

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
	if os.environ.get("ENV_NAME").upper() == "PROD":
		ToEmailAddr = ToEmailAddr 
	else:
		_logger.debug('Non prod environment detected. So sending emails to rkanade@gmail.com instead of %s', ToEmailAddr)
		ToEmailAddr = 'rkanade@gmail.com' #ToEmailAddr -> done purposefully to avoid sending emails to

	_logger.info("Setting up SMTP server again")

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

def downloadResumeFromLink(subject, emailBody, from_email_addr,userID):
	
	try:
		soup = BeautifulSoup(emailBody,"html.parser")
		temp_name = None
		links = soup.find_all('a',  attrs={'href': re.compile("^https://www.linkedin.com")})
		print(links)
		for link in links:
			# display the actual urls
			try:
				_logger.debug(link.getText())
				if link.getText().find('Download') != -1 :
					print('Download link found')

					url = link.get('href')

					#print(link.get('href'))
					r = requests.get(url, allow_redirects=True)
					temp_name = constants.getUploadFolderPath() + next(tempfile._get_candidate_names()) + ".unknown"

					f = open(temp_name ,'wb' )
					f.write(r.content)
					f.close()
					r.close()

					fileTypes = {	'application/pdf' : 'pdf',
									'application/vnd.openxmlformats-officedocument.wordprocessingml.document' : 'docx'
									}
					#print(magic.from_buffer(f, mime=True))
					extMimeType = magic.from_file(temp_name, mime=True)
					new_ext = fileTypes.get(extMimeType,'unknown')

					pre, ext = os.path.splitext(temp_name)
					os.rename(temp_name, pre + "." + new_ext)
					temp_name = pre + "." + new_ext

					#if new_ext is unknown delete the file else send the downloaded file further
					(retcode, msg, resumeId) = process_single_file(temp_name,userID)
					# Save resume has failed so send email , log error and continue to next attachment
					if retcode != resumeUtils.RetCodes.success.value:
						_logger.warning("Failed to save file {0} as resume".format(temp_name))
						sendMail(from_email_addr,'Resume upload failure notification',
							"Failed to save file {0} as resume".format(temp_name),'plain')
						continue
					else:	
						# see if jobID is mentioned in subject and if yes auto shortlist
						jobID = extractJobIdFromSubject( subject)
						shortlistDownloadedResumes(jobID,resumeId,userID)

						# Send success resume save email
						file_loader = FileSystemLoader('./conf')
						env = Environment(loader=file_loader)
						template = env.get_template('resume_upload_response.template')		
						body = template.render(resumeID = resumeId )
						sendMail(from_email_addr,'Resume upload notification',body,'plain')
						break
					
			except Exception as e:
				_logger.error("Exception occured while processing resume downloaded via links.",exc_info=1)
			finally:
				if temp_name is not None and os.path.exists(temp_name):
					os.remove(temp_name)	
	except Exception as e1:
		_logger.error("Exception occured while trying to download resumes shared as links.",exc_info=1)


def extractJobIdFromSubject( subject):
	if subject.strip().isdigit():
		return int(subject.strip())
	else:
		return None

def shortlistDownloadedResumes(jobID,resumeID,userID):
	if ( jobID != None):

		resultTuple = jdUtils.shortlist(resumeID,jobID,
							datetime.now(tz=timezone.utc),0,userID)


		if resultTuple[0] == jdUtils.RetCodes.success.value :
			_logger.info(f"Resume ID {resumeID} successfully shortlisted for Job id {jobID}")
		else:
			_logger.info(f"Failed to shortlist Resume ID {resumeID} for Job id {jobID}")
		
		return resultTuple

	else:
		_logger.debug(f"Job ID can not be {jobID} for shortlisting")
		return (None,'Job ID can not be None', None )


if __name__ == "__main__":

	#sendMail('rrkanade22@yahoo.com', "test subject", "test body",'plain')
	#time.sleep(60)
	
	#while True:
	logging.basicConfig(level=logging.DEBUG)
	readEmails()
	#print ( extractJobIdFromSubject(" rajesh ") )

	exit(0)

	#	time.sleep(60)
	email_body = """
		<tr>
		<td style="border-radius:2px;padding:6px 16px;color:#004b7c;font-weight:500;font-size:16px;border-color:#004b7c;border-width:1px;border-style:solid">
		<a href="https://www.linkedin.com/e/v2?e=-uyw9c2-l4dokbn6-4y&amp;lipi=urn%3Ali%3Apage%3Aemail_email_jobs_new_applicant_01%3BF%2BS6P08USNi5Ay12eizreQ%3D%3D&amp;t=plh&amp;ek=email_jobs_new_applicant_01&amp;li=0&amp;m=email_jobs_new_applicant&amp;ts=job_posting_download_resume&amp;urlhash=0Sa0&amp;url=https%3A%2F%2Fwww%2Elinkedin%2Ecom%2Ftalent%2Fapi%2FtalentResumes%3FapplicationId%3D12015992903%26tokenId%3D2590521057%26checkSum%3DAQGk7zwBbC14see7gx7OOC_jC0A8eqsuz2I" style="color:#004b7c;display:inline-block;text-decoration:none" target="_blank" data-saferedirecturl="https://www.google.com/url?hl=en&amp;q=https://www.linkedin.com/e/v2?e%3D-uyw9c2-l4dokbn6-4y%26lipi%3Durn%253Ali%253Apage%253Aemail_email_jobs_new_applicant_01%253BF%252BS6P08USNi5Ay12eizreQ%253D%253D%26t%3Dplh%26ek%3Demail_jobs_new_applicant_01%26li%3D0%26m%3Demail_jobs_new_applicant%26ts%3Djob_posting_download_resume%26urlhash%3D0Sa0%26url%3Dhttps%253A%252F%252Fwww%252Elinkedin%252Ecom%252Ftalent%252Fapi%252FtalentResumes%253FapplicationId%253D12015992903%2526tokenId%253D2590521057%2526checkSum%253DAQGk7zwBbC14see7gx7OOC_jC0A8eqsuz2I&amp;source=gmail&amp;ust=1655464836716000&amp;usg=AOvVaw3TvZCF5U_BHnLoHtcu0f9n">Download
		resume</a></td>
		</tr>
		</tbody>
		</table>
		</a></td>
		</tr>
		</tbody>
		</table>
		<table border="0" cellpadding="0" cellspacing="0" style="display:inline-block">
		<tbody>
		<tr>
		<td align="center" valign="middle"><a href="https://www.linkedin.com/comm/hiring/jobs/3107714910/applicants/12015992903/detail/?trk=eml-email_jobs_new_applicant_01-email_jobs_new_applicant-13-hiring_profile_application&amp;trkEmail=eml-email_jobs_new_applicant_01-email_jobs_new_applicant-13-hiring_profile_application-null-%7Euyw9c2%7El4dokbn6%7E4y-null-neptune%2Fhiring%2Ejobs%2Ejob%2Eapplicant%2Edetail&amp;lipi=urn%3Ali%3Apage%3Aemail_email_jobs_new_applicant_01%3BF%2BS6P08USNi5Ay12eizreQ%3D%3D" style="word-wrap:normal;color:#0073b1;word-break:normal;white-space:nowrap;display:block;text-decoration:none" target="_blank" data-saferedirecturl="https://www.google.com/url?hl=en&amp;q=https://www.linkedin.com/comm/hiring/jobs/3107714910/applicants/12015992903/detail/?trk%3Deml-email_jobs_new_applicant_01-email_jobs_new_applicant-13-hiring_profile_application%26trkEmail%3Deml-email_jobs_new_applicant_01-email_jobs_new_applicant-13-hiring_profile_application-null-%257Euyw9c2%257El4dokbn6%257E4y-null-neptune%252Fhiring%252Ejobs%252Ejob%252Eapplicant%252Edetail%26lipi%3Durn%253Ali%253Apage%253Aemail_email_jobs_new_applicant_01%253BF%252BS6P08USNi5Ay12eizreQ%253D%253D&amp;source=gmail&amp;ust=1655464836716000&amp;usg=AOvVaw1h7ccZ0cSv2Q_CtFzifx6w">
		<table role="presentation" border="0" cellspacing="0" cellpadding="0" width="auto">
		<tbody>
		<tr>
		<td bgcolor="#004b7c" style="padding:6px 16px;color:#ffffff;font-weight:500;font-size:16px;border-color:#004b7c;background-color:#004b7c;border-radius:2px;border-width:1px;border-style:solid">
		<a href="https://www.linkedin.com/comm/hiring/jobs/3107714910/applicants/12015992903/detail/?trk=eml-email_jobs_new_applicant_01-email_jobs_new_applicant-13-hiring_profile_application&amp;trkEmail=eml-email_jobs_new_applicant_01-email_jobs_new_applicant-13-hiring_profile_application-null-%7Euyw9c2%7El4dokbn6%7E4y-null-neptune%2Fhiring%2Ejobs%2Ejob%2Eapplicant%2Edetail&amp;lipi=urn%3Ali%3Apage%3Aemail_email_jobs_new_applicant_01%3BF%2BS6P08USNi5Ay12eizreQ%3D%3D" style="color:#ffffff;display:inline-block;text-decoration:none" target="_blank" data-saferedirecturl="https://www.google.com/url?hl=en&amp;q=https://www.linkedin.com/comm/hiring/jobs/3107714910/applicants/12015992903/detail/?trk%3Deml-email_jobs_new_applicant_01-email_jobs_new_applicant-13-hiring_profile_application%26trkEmail%3Deml-email_jobs_new_applicant_01-email_jobs_new_applicant-13-hiring_profile_application-null-%257Euyw9c2%257El4dokbn6%257E4y-null-neptune%252Fhiring%252Ejobs%252Ejob%252Eapplicant%252Edetail%26lipi%3Durn%253Ali%253Apage%253Aemail_email_jobs_new_applicant_01%253BF%252BS6P08USNi5Ay12eizreQ%253D%253D&amp;source=gmail&amp;ust=1655464836716000&amp;usg=AOvVaw1h7ccZ0cSv2Q_CtFzifx6w">View
		full application</a></td>
		</tr>
	"""
	downloadResumeFromLink(email_body)


