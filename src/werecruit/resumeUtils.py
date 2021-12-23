import dbUtils
import constants

from datetime import datetime
from datetime import timezone

import docx2txt
import re
#import docx
import os.path
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

import en_core_web_sm
import spacy

from spacy.matcher import PhraseMatcher
from spacy.matcher import Matcher

import unicodedata
import logging
logging.getLogger("pdfminer").setLevel(logging.WARNING)

_logger = logging.getLogger('resumeUtils')
_nlp = spacy.load("en_core_web_sm")


from enum import Enum
class RetCodes(Enum):
	success = 'RES_CRUD_S200'
	missing_ent_attrs_error = "RES_CRUD_E400"
	empty_ent_attrs_error = "RES_CRUD_E401"
	save_ent_error = "RES_CRUD_E403"
	del_ent_error = "RES_CRUD_E404"
	get_ent_error = "RES_CRUD_E405"
	server_error = "RES_CRUD_E500"

class ResumeStatusCodes(Enum):
	active = 0
	inactive = 1

class ApplicationStatusCodes(Enum):
	shortlisted = 0
	round1_interview_scheduled = 10
	round1_interview_cleared = 20
	round1_interview_failed = 30
	round1_interview_failed_noshow = 31
	round2_interview_scheduled = 40
	round2_interview_cleared = 50
	round2_interview_failed = 60
	round2_interview_failed_noshow = 61
	hiring_mgr_interview_scheduled = 70
	hiring_mgr_interview_cleared = 80
	hiring_mgr_interview_failed = 90
	hiring_mgr_interview_failed_noshow = 91
	hr_interview_scheduled = 100
	hr_interview_cleared = 110
	hr_interview_failed = 120
	hr_interview_failed_noshow = 121
	offer_pending =130
	offer_released = 140
	offer_accepted = 150
	candidate_joined = 160
	candidate_noshow = 170

ApplicationStatusNames = {
	ApplicationStatusCodes.shortlisted.value : 'Shortlisted',
	ApplicationStatusCodes.round1_interview_scheduled.value : 'Round 1 interview scheduled',
	ApplicationStatusCodes.round1_interview_cleared.value : 'Round 1 interview cleared',
	ApplicationStatusCodes.round1_interview_failed.value :  'Round 1 interview failed',
	ApplicationStatusCodes.round1_interview_failed_noshow.value : 'Round 1 interview No-show',
	ApplicationStatusCodes.round2_interview_scheduled.value : 'Round 2 interview scheduled',
	ApplicationStatusCodes.round2_interview_cleared.value : 'Round 2 interview cleared',
	ApplicationStatusCodes.round2_interview_failed.value : 'Round 2 interview failed',
	ApplicationStatusCodes.round2_interview_failed_noshow.value : 'Round 2 interview No-show',
	ApplicationStatusCodes.hiring_mgr_interview_scheduled.value : 'Hiring manager interview scheduled',
	ApplicationStatusCodes.hiring_mgr_interview_cleared.value : 'Hiring manager interview cleared', 
	ApplicationStatusCodes.hiring_mgr_interview_failed.value : 'Hiring manager interview failed',
	ApplicationStatusCodes.hiring_mgr_interview_failed_noshow.value : 'Hiring manager interview No-show',
	ApplicationStatusCodes.hr_interview_scheduled.value : 'HR interview scheduled',
	ApplicationStatusCodes.hr_interview_cleared.value : 'HR interview cleared',
	ApplicationStatusCodes.hr_interview_failed.value : 'HR interview failed',
	ApplicationStatusCodes.hr_interview_failed_noshow.value : 'HR interview No-show',
	ApplicationStatusCodes.offer_pending.value : 'Offer pending to candidate',
	ApplicationStatusCodes.offer_released.value :'Offer released to candidate',
	ApplicationStatusCodes.offer_accepted.value :  'Offer accepted by candidate'		
	}


def save_resume(id, fileName, candidateName,candidateEmail,candidatePhone, recruiterID):
	_logger.debug('inside save_resume function')
	db_con = dbUtils.getConnFromPool()
	cursor = db_con.cursor()
	try:
		_logger.info(candidateName)
		if not bool(candidateName):
			 return(RetCodes.empty_ent_attrs_error.value,"Candidate Name empty or null.", None)
		
		_logger.info(candidateEmail)
		if not bool(candidateEmail):
			 return(RetCodes.empty_ent_attrs_error.value,"Candidate Email empty or null.", None)

		if not bool(candidatePhone):
			 return(RetCodes.empty_ent_attrs_error.value,"Candidate Phone empty or null.", None)

		if not recruiterID:
			 return(RetCodes.empty_ent_attrs_error.value,"Recruiter ID field is empty or null.", None)


		if (int(id) == constants.NEW_ENTITY_ID):
			##insert a record in user table
			sql = """insert into public.wr_resumes ( resume_filename, name, email, 
					phone, recruiter_id ) 
					values (%s,%s,%s,
					%s,%s) returning id """
			
			params = (fileName,candidateName,candidateEmail,
					candidatePhone,int(recruiterID))

			_logger.debug ( cursor.mogrify(sql, params))
			
			cursor.execute(sql, params)
			assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

			result = cursor.fetchone()
			resume_id = result[0]
			_logger.debug ("Resume id {} successfully created.".format(resume_id))

			db_con.commit()
			return (RetCodes.success.value, "Resume id {} successfully uploaded.".format(resume_id), resume_id)
		else:
			sql = """update public.wr_resumes set  
						name = %s,  email = %s, phone = %s,
						recruiter_id = %s
					where id = %s"""
			params = (candidateName,candidateEmail, candidatePhone,
						recruiterID,
						int(id))
						
			_logger.debug ( cursor.mogrify(sql, params))
			
			cursor.execute(sql, params)
			assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

			if fileName != None:
				sql1 = """update public.wr_resumes set  
						resume_filename = %s
					where id = %s"""
				params1 = (fileName,
						int(id))
				cursor.execute(sql1, params1)
				assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."
				
			_logger.debug ("Resume id {0} updated successfully.".format(id) )
		
			db_con.commit()
			return (RetCodes.success.value, "Resume id {0} updated successfully.".format(id),id)
			
	except Exception as e:
		_logger.error(e)
		db_con.rollback()
		return (RetCodes.server_error.value, str(e),None)
	
	finally:
		if cursor is not None:
			cursor.close()
		dbUtils.returnToPool(db_con)

def list_resumes_by_recruiter(recruiterID):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		
		query = """SELECT * FROM wr_resumes 
				where recruiter_id = %s order by id desc"""
	
		params = (recruiterID,)
		_logger.debug ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		resumeList =cursor.fetchall()

		return(RetCodes.success.value, "Resume List successfully fetched from db", resumeList)


	except Exception as dbe:
		_logger.error(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	

def list_resumes_by_tenant(tenantID):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		
		query = """SELECT * FROM wr_resumes 
				where recruiter_id in ( select uid from tenant_user_roles where tid = %s) 
				order by id desc"""
	
		params = (tenantID,)
		_logger.debug ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		resumeList =cursor.fetchall()

		return(RetCodes.success.value, "Resume List successfully fetched from db for tenant ID {0}".format(tenantID), resumeList)

	except Exception as dbe:
		_logger.error(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	

def list_application_status_codes():
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		
		query = """SELECT * FROM application_status_codes
					order by id asc"""
	
		#params = (recruiterID,)
		_logger.debug ( cursor.mogrify(query, ))
		cursor.execute(query,)

		appStatusCodesList =cursor.fetchall()

		return(RetCodes.success.value, "Application status code List successfully fetched from db", appStatusCodesList)


	except Exception as dbe:
		_logger.error(dbe)
		return ( RetCodes.server_error.value, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	

def get(id):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		
		query = """SELECT * FROM wr_resumes 
				where id = %s"""
	
		params = (id,)
		_logger.debug ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		assert cursor.rowcount == 1, "assertion failed : Effected row count is not equal to 1."

		resume = cursor.fetchone()

		return(RetCodes.success.value, "Resume  for id {0} successfully fetched from db".format(id), resume)


	except Exception as dbe:
		_logger.debug(dbe)
		return ( RetCodes.server_error.value, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	


def process_single_resume( testResumeFileName ):
		
	ext = getFileExtension(testResumeFileName)

	#_logger.debug(ext)
	#_logger.debug("Extension found is", ext)
	resumeText=''

	if ext == 'docx':
		resumeText = readDocx(testResumeFileName)
	elif ext == 'pdf': 
		resumeText = readPDF(testResumeFileName)
	else:
		return

	#wordTokenizer(resumeText)
	#_summary_list.append({"resume-file-name": testResumeFileName})
	#_summary_list['resume-file-name'] = testResumeFileName
	#_summary_list.append({"res-text": resumeText})

	_logger.debug("\n\n *************** Text resume after rmoving special chars ************* \n\n ")
	resumeText = clean_text(resumeText)

	_logger.debug(resumeText)

	name = extract_full_name(resumeText)
	#extract_full_name1(resumeText)
	phone=extract_phones(resumeText)
	email = extract_emails(resumeText)
	
	'''print(name)
	print(email)
	print(phone)'''

	return(name,email,phone)

def readPDF(pdf_file_name):
	rsrcmgr = PDFResourceManager()
	retstr = StringIO()
	codec = 'utf-8'
	laparams = LAParams()
	device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
	fp = open(pdf_file_name, 'rb')
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	password = ""
	maxpages = 0
	caching = True
	pagenos=set()

	for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
		interpreter.process_page(page)

	text = retstr.getvalue()

	fp.close()
	device.close()
	retstr.close()

	return text

def readDocx(doc_file_name):
	_logger.debug(doc_file_name)
	text = docx2txt.process(doc_file_name)
	return(text)


## get file extension
def getFileExtension ( fileName):
	extension = os.path.splitext(fileName)[1][1:]
	return extension

def clean_text(text):
	#resumeText = resumeText.replace("\r", ' ')
	#resumeText = resumeText.replace("\n", ' ')
	text = text.replace("\t", ' ')
	text = text.replace("\n", ' ')

	#text = text.replace("-", ' ')


	text = re.sub(r'[^\x00-\x7F]+', ' ', text)
	#resumeText = re.sub(r'[^\\x00-\\x7F]+', '', resumeText)

	text = unicodedata.normalize("NFKD",text)
	#_summary_list.append({"cleaned-res-text": text})

	return text

def extract_emails(text):
	
	emailMatcher = Matcher(_nlp.vocab,True)
	doc = _nlp(text)

	_logger.debug ("****** Get Email address ")
	emailMatcher.add("email",[[{"LIKE_EMAIL" : True}]],on_match=None)
	matches = emailMatcher(doc)  #EMail matcher
	results = []
	for match_id, start, end in matches:
		rule_id = _nlp.vocab.strings[match_id]  # get the unicode ID, i.e. 'COLOR'
		span = doc[start : end]  # get the matched slice of the doc
		_logger.debug("Email Found : " , span.text)
		#logger.info("EMail Found : %s " , span.text)
		if span.text.lower() not in results:
			results.append(span.text.lower())

	return results
	#_summary_list.append({"Emails":results})
	#_summary_list['Emails'] = results

def extract_phones(text):
	
	doc = _nlp(text)
	
	_logger.debug ("****** Get Phone ************* ")
	matcher = Matcher(_nlp.vocab,True)

	pattern = [{"LIKE_NUM": True, "LENGTH":10}]
	matcher.add("phone",[pattern],on_match=None)

	results =[]
	matches = matcher(doc)  #Phone phrase matcher
	for match_id, start, end in matches:
		rule_id = _nlp.vocab.strings[match_id]  # get the unicode ID, i.e. 'COLOR'
		span = doc[start : end]  # get the matched slice of the doc
		#logger.info("phone Found : %s " , span.text)
		if span.text.lower() not in results:
			results.append(span.text.lower())
		#results.append(span.text)


	pMatcher = PhraseMatcher(_nlp.vocab, attr="SHAPE")

	pattern = _nlp('0123456789')
	pMatcher.add("PHONE_NUMBER", None, pattern)

	pattern = _nlp('+91 0123456789')    
	pMatcher.add("PHONE_NUMBER", None, pattern)

	pattern = _nlp('+91-0123456789')
	pMatcher.add("PHONE_NUMBER", None, pattern)
	
	matches = pMatcher(doc)  #Phone phrase matcher
	for match_id, start, end in matches:
		rule_id = _nlp.vocab.strings[match_id]  # get the unicode ID, i.e. 'COLOR'
		span = doc[start : end]  # get the matched slice of the doc
		#logger.info("phone Found : %s " , span.text)
		if  len(span.text) >= 10 :
			#results.append(span.text)
			if span.text.lower() not in results:
				results.append(span.text.lower())
			break
	
	return results

	#_summary_list.append({"Phones":results})
	#_summary_list['Phones'] = results

def extract_full_name(text):
	doc = _nlp(text)
	matcher = Matcher(_nlp.vocab,True)

	pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
	matcher.add('FULL_NAME',[pattern],on_match=None)
	
	results = []
	matches = matcher(doc)
	for match_id, start, end in matches:
		span = doc[start:end]
		_logger.debug ("Full Name is " + span.text)
		#logger.info("Full Name : %s " , span.text)

		#this is added to ensure if someone has added F Name M Name L Name, then we need to fetch the immediate next word if it proper noun 
		tokens = [token for token in doc]

		t = tokens[end] #get the next word

		_logger.debug(t.text)
		_logger.debug(t.pos_)
		if ( str(t.pos_) == 'PROPN'):
			_logger.debug( span.text + " " + t.text )
			results.append(span.text + " " + t.text )

		else:
			_logger.debug( span.text)
			results.append(span.text)

		break 
	
	return results

	#_summary_list.append({"Name":results})
	#_summary_list['Name'] = results

def extract_full_name1(text):
	
	doc = _nlp(text)
	results =[]
	for sent in doc.sents:
		#if len(results) > 0:
		#    break
		doc1 = _nlp(sent.text.lower())
		for ent in doc1.ents:
			if (ent.label_ == 'PERSON'):
				results.append(ent.text)

## main entry point
if __name__ == "__main__":
	#(retCode,msg,data) = save_resume(constants.NEW_ENTITY_ID,None,'rajesh','rkanade@gmail.com','9890303698',1)
	#_logger.debug(retCode)
	#_logger.debug(msg)
	#shortlist(25,[17], datetime.now(tz=timezone.utc),
	#	ApplicationStatusCodes.shortlisted.value,1)

	logging.basicConfig(level = logging.DEBUG)
	
	(name,email,phone) = process_single_resume('C:\\Users\\rajesh\\Downloads\\AK.pdf')
	
	_logger.debug(name)
	_logger.debug(email)
	_logger.debug(phone)



