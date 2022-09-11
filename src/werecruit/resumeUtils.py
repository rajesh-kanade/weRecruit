from enum import Enum
from itertools import count
from multiprocessing.util import NOTSET
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

import json

import unicodedata

import userUtils
import jdUtils

import logging
logging.getLogger("pdfminer").setLevel(logging.WARNING)

#from dotenv import load_dotenv , find_dotenv
# load_dotenv(find_dotenv())
#logging.basicConfig(format=constants.LOG_FORMAT, level=int(os.environ.get("LOG_LEVEL",20)))

_logger = logging.getLogger()
_nlp = spacy.load("en_core_web_sm")


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
	auto_shortlisted = -1 
	shortlisted = 0

	initial_screen_scheduled = 1
	initial_screen_cleared = 2
	initial_screen_failed = 3
	initial_screen_failed_noshow = 4
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
	offer_pending = 130
	offer_released = 140
	offer_accepted = 150
	candidate_joined = 160
	candidate_noshow = 170


ApplicationStatusNames = {
	ApplicationStatusCodes.shortlisted.value: 'Shortlisted',
	ApplicationStatusCodes.round1_interview_scheduled.value: 'Round 1 interview scheduled',
	ApplicationStatusCodes.round1_interview_cleared.value: 'Round 1 interview cleared',
	ApplicationStatusCodes.round1_interview_failed.value:  'Round 1 interview failed',
	ApplicationStatusCodes.round1_interview_failed_noshow.value: 'Round 1 interview No-show',
	ApplicationStatusCodes.round2_interview_scheduled.value: 'Round 2 interview scheduled',
	ApplicationStatusCodes.round2_interview_cleared.value: 'Round 2 interview cleared',
	ApplicationStatusCodes.round2_interview_failed.value: 'Round 2 interview failed',
	ApplicationStatusCodes.round2_interview_failed_noshow.value: 'Round 2 interview No-show',
	ApplicationStatusCodes.hiring_mgr_interview_scheduled.value: 'Hiring manager interview scheduled',
	ApplicationStatusCodes.hiring_mgr_interview_cleared.value: 'Hiring manager interview cleared',
	ApplicationStatusCodes.hiring_mgr_interview_failed.value: 'Hiring manager interview failed',
	ApplicationStatusCodes.hiring_mgr_interview_failed_noshow.value: 'Hiring manager interview No-show',
	ApplicationStatusCodes.hr_interview_scheduled.value: 'HR interview scheduled',
	ApplicationStatusCodes.hr_interview_cleared.value: 'HR interview cleared',
	ApplicationStatusCodes.hr_interview_failed.value: 'HR interview failed',
	ApplicationStatusCodes.hr_interview_failed_noshow.value: 'HR interview No-show',
	ApplicationStatusCodes.offer_pending.value: 'Offer pending to candidate',
	ApplicationStatusCodes.offer_released.value: 'Offer released to candidate',
	ApplicationStatusCodes.offer_accepted.value:  'Offer accepted by candidate'
}

# primarly called from resume parser


def update_resume(id, resume_attr_list):

	_logger.debug('inside update_resume function')
	db_con = dbUtils.getConnFromPool()
	cursor = db_con.cursor()

	try:
		_logger.debug(id)
		if not bool(id):
			return(RetCodes.empty_ent_attrs_error.value, "Resume ID is empty or null.", None)

		_logger.debug(resume_attr_list)
		if not bool(resume_attr_list):
			return(RetCodes.empty_ent_attrs_error.value, "Resume attribute list empty or null.", None)

		# resume parser returns list of potential matches for name , phone, email.
		# Update the first one else ask user to update manually.
		if bool(resume_attr_list['name']):
			name = resume_attr_list['name'][0]
		else:
			name = 'Resume parser can not update this field.Manual update required.'

		if bool(resume_attr_list['phone']):
			phone = resume_attr_list['phone'][0]
		else:
			phone = 'Resume parser can not update this field.Manual update required.'

		if bool(resume_attr_list['email']):
			email = resume_attr_list['email'][0]
		else:
			email = 'Resume parser can not update this field.Manual update required.'

		json_resume = json.dumps(resume_attr_list, indent=4, sort_keys=False)

		sql = """update public.wr_resumes set  
					name = %s,  email = %s, phone = %s,
						json_resume = %s
					where id = %s"""
		params = (name, email, phone,
				  json_resume,
				  int(id))

		_logger.debug(cursor.mogrify(sql, params))

		cursor.execute(sql, params)
		assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

		_logger.debug("Resume id {0} updated successfully.".format(id))

		db_con.commit()
		return (RetCodes.success.value, "Resume id {0} updated successfully.".format(id), id)

	except Exception as e:
		_logger.error(e)
		db_con.rollback()
		return (RetCodes.server_error.value, str(e), None)

	finally:
		if cursor is not None:
			cursor.close()
		dbUtils.returnToPool(db_con)


def save_resume(id, fileName, candidateName, candidateEmail, candidatePhone, recruiterID, notes=None):
	_logger.debug('inside save_resume function')
	db_con = dbUtils.getConnFromPool()
	cursor = db_con.cursor()
	try:
		_logger.info(candidateName)
		if not candidateName.strip():
			return(RetCodes.empty_ent_attrs_error.value, "Name cannot be blank/Please enter your name.", None)

		_logger.info(candidateEmail)
		if not candidateEmail.strip():
			return(RetCodes.empty_ent_attrs_error.value, "Please enter your Email", None)

		if not candidatePhone.strip():
			return(RetCodes.empty_ent_attrs_error.value, "Phone number cannot be blank", None)

		if not recruiterID:
			return(RetCodes.empty_ent_attrs_error.value, "Recruiter ID field is empty or null.", None)
		
		_logger.debug('Resume file name is {0}'.format(fileName))
		if (fileName is None):
			file_data = None
			json_resume = None
		else:
			file_data = bytes(open(fileName, "rb").read())
			(resume_attr_list) = process_single_resume(fileName)
			
			json_resume = json.dumps(
				resume_attr_list, indent=4, sort_keys=False)
	  
		if (int(id) == constants.NEW_ENTITY_ID):
			# insert a record in user table
			sql = """insert into public.wr_resumes ( resume_filename, name, email, 
					phone, recruiter_id, resume_content, json_resume,
					notes, creation_date) 
					values (%s,%s,%s,
					%s,%s,%s,%s,%s,%s) returning id """

			params = (fileName, candidateName, candidateEmail,
					  candidatePhone, int(recruiterID), file_data, json_resume, 
					  notes, datetime.now(tz=timezone.utc))
					

			_logger.debug(cursor.mogrify(sql, params))

			cursor.execute(sql, params)
			assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

			result = cursor.fetchone()
			resume_id = result[0]
			_logger.debug(
				"Resume id {} successfully created.".format(candidateName))

			db_con.commit()
			return (RetCodes.success.value, "Resume for Candidate '{}' successfully uploaded.".format(candidateName),resume_id)
		else:
			# When record is updated, resume can be left null or can be uploaded with a new or same resume.
			# Handle resume upload case seperately...
			# TODO rewrite this block in a better way
			sql = """update public.wr_resumes set  
						name = %s, email = %s, phone = %s,
						recruiter_id = %s, notes = %s, updation_date = %s
					where id = %s"""
			params = (candidateName, candidateEmail, candidatePhone,
					  recruiterID, notes, datetime.now(tz=timezone.utc),
					  int(id))

			_logger.debug(cursor.mogrify(sql, params))

			cursor.execute(sql, params)
			assert cursor.rowcount == 1, "assert failed : Row Effected is not equal to 1."

			# TODO -> Think of better way to do this
			# New resume file is uploaded then we will store the parsed json_resume again
			# if fileName != None:
			sql1 = """update public.wr_resumes set  
						resume_filename = %s,resume_content = %s,json_resume = %s
					where id = %s"""
			params1 = (fileName, file_data, json_resume,
						   int(id))
			cursor.execute(sql1, params1)
			assert cursor.rowcount == 1, "assert failed : Row Effected is not equal to 1."

			db_con.commit()
			_logger.debug("Resume id {0} updated successfully.".format(id))
			return (RetCodes.success.value, "Resume id {0} updated successfully.".format(id), id)

	except Exception as e:
		_logger.error(e)
		db_con.rollback()
		return (RetCodes.server_error.value, str(e), None)

	finally:
		if cursor is not None:
			cursor.close()
		dbUtils.returnToPool(db_con)


'''
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
'''


def list_resumes_by_tenant(tenantID, orderBy=None, order=None):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)

		q1 = """SELECT * , 
				(select skillset_name from skillsets where id = CAST(json_resume->'top_skills'->>0 AS INTEGER) ) as topskill1, 
				(select skillset_name from skillsets where id = CAST(json_resume->'top_skills'->>1 AS INTEGER) ) as topskill2, 
				(select skillset_name from skillsets where id = CAST(json_resume->'top_skills'->>2 AS INTEGER) ) as topskill3
				FROM wr_resumes
				where is_deleted = %s and
				recruiter_id in ( select uid from tenant_user_roles where tid = %s) order by """
		q2 = """ """
		q3 = """ name ASC """
		query, params = None, None
		if orderBy == "name":
			q2 = """ name, """
		query = q1 + q2 + q3
		params = (False, tenantID)
		_logger.debug(cursor.mogrify(query, params))
		cursor.execute(query, params)

		resumeList = cursor.fetchall()
		if order == "DESC":
			resumeList = resumeList[::-1]

		return (
			RetCodes.success.value,
			"Resume List successfully fetched from db for tenant ID {0}".format(
				tenantID
			),
			resumeList,
		)

	except Exception as dbe:
		_logger.error(dbe)
		return (RetCodes.server_error, str(dbe), None)

	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)

def search_resumes(tenantID, ftSearch,orderBy=None, order=None):
	try:

		if not bool(ftSearch):
			return(RetCodes.missing_ent_attrs_error.value, "Search criteria not specified.".format(tenantID), None)

		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)

		# to_tsvector('english',json_resume)
		# @@ to_tsquery('Java')


		kwrdList = ftSearch.split()
		_logger.debug("Keyword list for free text is as under %s", kwrdList)
		ft_cond_json_resume = ' AND '.join(
			"to_tsvector('english',json_resume) @@ to_tsquery('{0}')".format(word) for word in kwrdList)

		ft_cond_name = ' OR '.join(
			"to_tsvector('english',name) @@ to_tsquery('{0}')".format(word) for word in kwrdList)

		'''ft_cond = ""
		for word in kwrdList:
			ft_cond += "to_tsvector('english',json_resume) @@ to_tsquery('{0}')".format(word)
			ft_cond += " AND "
		'''

		_logger.debug("Full text search is %s OR %s", ft_cond_json_resume, ft_cond_name)

		query = """SELECT *,
				(select skillset_name from skillsets where id = CAST(json_resume->'top_skills'->>0 AS INTEGER) ) as topskill1, 
				(select skillset_name from skillsets where id = CAST(json_resume->'top_skills'->>1 AS INTEGER) ) as topskill2, 
				(select skillset_name from skillsets where id = CAST(json_resume->'top_skills'->>2 AS INTEGER) ) as topskill3
				FROM wr_resumes 
				where is_deleted = %s and
				recruiter_id in ( select uid from tenant_user_roles where tid = %s) 
				AND ( """ + str(ft_cond_json_resume) + " ) " + " OR ( " + str(ft_cond_name) + " ) "

		if not orderBy:
			orderCond =  " order by id desc"
		if orderBy == 'client':
			orderCond =  " order by name ASC"

		query = query + orderCond

		params = (False, tenantID)
		_logger.debug(cursor.mogrify(query, params))
		cursor.execute(query, params)

		resumeList = cursor.fetchall()
		if order == 'DESC':
			resumeList = resumeList[::-1]

		return(RetCodes.success.value, "Resume List successfully fetched from db for tenant ID {0}".format(tenantID), resumeList)

	except Exception as dbe:
		_logger.error(dbe, exc_info=True)
		return (RetCodes.server_error, str(dbe), None)

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
		_logger.debug(cursor.mogrify(query, ))
		cursor.execute(query,)

		appStatusCodesList = cursor.fetchall()

		return(RetCodes.success.value, "Application status code List successfully fetched from db", appStatusCodesList)

	except Exception as dbe:
		_logger.error(dbe)
		return (RetCodes.server_error.value, str(dbe), None)

	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)

def list_resume_application_status_codes_category():
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)

		query = """SELECT * FROM resume_application_status_codes_category
					ORDER BY id ASC"""

		#params = (recruiterID,)
		_logger.debug(cursor.mogrify(query, ))
		cursor.execute(query,)

		appStatusCodesCatList = cursor.fetchall()

		return(RetCodes.success.value, "Resume application status code List successfully fetched from db", appStatusCodesCatList)

	except Exception as dbe:
		_logger.error(dbe)
		return (RetCodes.server_error.value, str(dbe), None)

	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)


def list_resume_application_status_codes_sub_category(category_id):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)

		query = """SELECT * FROM resume_application_status_codes_sub_category
					WHERE category_id = %s
					ORDER BY id ASC"""

		params = (category_id,)
		_logger.debug(cursor.mogrify(query, params))
		cursor.execute(query, params)

		appStatusCodesSubCatList = cursor.fetchall()

		return(RetCodes.success.value, "Resume application status code List successfully fetched from db", appStatusCodesSubCatList)

	except Exception as dbe:
		_logger.error(dbe)
		return (RetCodes.server_error.value, str(dbe), None)

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
		_logger.debug(cursor.mogrify(query, params))
		cursor.execute(query, params)

		assert cursor.rowcount == 1, "assert failed : Effected row count is not equal to 1."

		resume = cursor.fetchone()

		return(RetCodes.success.value, "Resume  for id {0} successfully fetched from db".format(id), resume)

	except Exception as dbe:
		_logger.debug(dbe)
		return (RetCodes.server_error.value, str(dbe), None)

	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)


def process_single_resume(testResumeFileName):

	#resumefolder = "./src/werecruit/resume_uploads/"
	ext = getFileExtension(testResumeFileName)

	# _logger.debug(ext)
	#_logger.debug("Extension found is", ext)
	resumeText = ''

	if ext == 'docx':
		rawText = readDocx(testResumeFileName)
	elif ext == 'pdf':
		rawText = readPDF(testResumeFileName)
	else:
		raise Exception('unsupported resume file type {0}'.format(ext))

	# wordTokenizer(resumeText)
	#_summary_list.append({"resume-file-name": testResumeFileName})
	#_summary_list['resume-file-name'] = testResumeFileName
	#_summary_list.append({"res-text": resumeText})

	_logger.debug(
		"\n\n *************** Text resume after removing special chars ************* \n\n ")
	resumeText = clean_text(rawText)

	_logger.debug(resumeText)

	name = extract_full_name(resumeText)
	# extract_full_name1(resumeText)
	phone = extract_phones(resumeText)
	email = extract_emails(resumeText)
	top_skills = extract_skills(resumeText)

	json_list = {}
	# dt_string
	json_list['processed-date'] = str(datetime.now(tz=timezone.utc))
	json_list['raw-text'] = rawText
	json_list['name'] = name
	json_list['phone'] = phone
	json_list['email'] = email
	json_list['top_skills'] = top_skills

	'''print(name)
	print(email)
	print(phone)'''

	return(json_list)


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
	pagenos = set()

	for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=True):
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


# get file extension
def getFileExtension(fileName):
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

	text = unicodedata.normalize("NFKD", text)
	#_summary_list.append({"cleaned-res-text": text})

	return text


def extract_emails(text):

	emailMatcher = Matcher(_nlp.vocab, True)
	doc = _nlp(text)

	_logger.debug("****** Get Email address ")
	emailMatcher.add("email", [[{"LIKE_EMAIL": True}]], on_match=None)
	matches = emailMatcher(doc)  # EMail matcher
	results = []
	for match_id, start, end in matches:
		# get the unicode ID, i.e. 'COLOR'
		rule_id = _nlp.vocab.strings[match_id]
		span = doc[start: end]  # get the matched slice of the doc
		_logger.debug("Email Found : %s ", span.text)
		#logger.info("EMail Found : %s " , span.text)
		if span.text.lower() not in results:
			results.append(span.text.lower())

	return results
	# _summary_list.append({"Emails":results})
	#_summary_list['Emails'] = results


def extract_phones(text):

	doc = _nlp(text)

	_logger.debug("****** Get Phone ************* ")
	matcher = Matcher(_nlp.vocab, True)

	pattern = [{"LIKE_NUM": True, "LENGTH": 10}]
	matcher.add("phone", [pattern], on_match=None)

	results = []
	matches = matcher(doc)  # Phone phrase matcher
	for match_id, start, end in matches:
		# get the unicode ID, i.e. 'COLOR'
		rule_id = _nlp.vocab.strings[match_id]
		span = doc[start: end]  # get the matched slice of the doc
		#logger.info("phone Found : %s " , span.text)
		if span.text.lower() not in results:
			results.append(span.text.lower())
		# results.append(span.text)

	pMatcher = PhraseMatcher(_nlp.vocab, attr="SHAPE")

	pattern = _nlp('0123456789')
	pMatcher.add("PHONE_NUMBER", None, pattern)

	pattern = _nlp('+91 0123456789')
	pMatcher.add("PHONE_NUMBER", None, pattern)

	pattern = _nlp('+91-0123456789')
	pMatcher.add("PHONE_NUMBER", None, pattern)

	matches = pMatcher(doc)  # Phone phrase matcher
	for match_id, start, end in matches:
		# get the unicode ID, i.e. 'COLOR'
		rule_id = _nlp.vocab.strings[match_id]
		span = doc[start: end]  # get the matched slice of the doc
		#logger.info("phone Found : %s " , span.text)
		if len(span.text) >= 10:
			# results.append(span.text)
			if span.text.lower() not in results:
				results.append(span.text.lower())
			break

	return results

	# _summary_list.append({"Phones":results})
	#_summary_list['Phones'] = results


def extract_full_name(text):
	doc = _nlp(text)
	matcher = Matcher(_nlp.vocab, True)

	pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
	matcher.add('FULL_NAME', [pattern], on_match=None)

	results = []
	matches = matcher(doc)
	for match_id, start, end in matches:
		span = doc[start:end]
		_logger.debug("Full Name is " + span.text)
		#logger.info("Full Name : %s " , span.text)

		# this is added to ensure if someone has added F Name M Name L Name, then we need to fetch the immediate next word if it proper noun
		tokens = [token for token in doc]

		t = tokens[end]  # get the next word

		_logger.debug(t.text)
		_logger.debug(t.pos_)
		if (str(t.pos_) == 'PROPN'):
			_logger.debug(span.text + " " + t.text)
			results.append(span.text + " " + t.text)

		else:
			_logger.debug(span.text)
			results.append(span.text)

		break

	return results

def extract_full_name1(text):

	doc = _nlp(text)
	results = []
	for sent in doc.sents:
		# if len(results) > 0:
		#    break
		doc1 = _nlp(sent.text.lower())
		for ent in doc1.ents:
			if (ent.label_ == 'PERSON'):
				results.append(ent.text)


def extract_skills(resumeText):
	
	text = resumeText

	matcher = Matcher(_nlp.vocab, True)
	pMatcher = PhraseMatcher( _nlp.vocab, attr="LOWER")

	db_con = dbUtils.getConnFromPool()
	cursor = dbUtils.getNamedTupleCursor(db_con)
	results_dict = {}

	sql = """
		SELECT * from skillsets
	"""
	_logger.debug(cursor.mogrify(sql))
	cursor.execute(sql)

	skillsetsList = cursor.fetchall()
	for skillset in skillsetsList:
		results_dict[str(skillset.id)] = []				
		_logger.debug("Fetching skills for skillset ID is %s", skillset.id)
		sql = """
			SELECT * from skills where skillset_id = %s
		"""
		params = (int(skillset.id),)
		_logger.debug(cursor.mogrify(sql,params))
		cursor.execute(sql,params)		

		skillList = cursor.fetchall()
		terms = []
		for skill in skillList:
			print(skill)
			matcher.add(skillset.id,[[{"LOWER" : skill.skill_name},{"IS_PUNCT": True}]])
			terms.append(skill.skill_name)

		# #Add all skills into Phrase matcher as well
		patterns = [_nlp.make_doc(text) for text in terms]
		pMatcher.add(str(skillset.id), None, *patterns)


	doc = _nlp(text)

	print(results_dict)

	matches = matcher(doc) #Token matcher
	for match_id, start, end in matches:
		rule_id = _nlp.vocab.strings[match_id]  
		span = doc[start : end]  # get the matched slice of the doc
		if str(rule_id) in results_dict.keys():
			results_dict[str(rule_id)].append(span.text)

	matches = pMatcher(doc)  #Phrase matcher
	for match_id, start, end in matches:
		rule_id = _nlp.vocab.strings[match_id]  
		span = doc[start : end]  # get the matched slice of the doc
		print("phrase matched : " , span.text)
		#weight = skillsets_df[skillsets_df.skillset_name.eq(rule_id),skillsets_df.skill_name.eq(span.text)]
		if str(rule_id) in results_dict.keys():
			results_dict[str(rule_id)].append(span.text)

	print( results_dict) 
	temp1 = {}
	for new_k, new_val in results_dict.items():
		print(new_k, len([item for item in new_val if item]))
		temp1.update({new_k: len([item for item in new_val if item])})
	temp2 = sorted(temp1.items(), key = lambda ele : temp1[ele[0]],reverse=True)
	
	print("The sorted dictionary is  " , temp2) 

	top_skills = [k[0] for k in temp2[:3] if k[1] > 0 ]
	print(top_skills)
	
	cursor.close()
	dbUtils.returnToPool(db_con)
	
	return top_skills

def populate_json_resumes():
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)

		query = """SELECT * FROM wr_resumes 
				where json_resume is null and resume_content is not null"""

		#params = (tenantID,)
		_logger.debug(cursor.mogrify(query))
		cursor.execute(query)

		resumeList = cursor.fetchall()
		for rec in resumeList:
			try:

				if rec.resume_content != None:
					# write the file to disk
					_logger.debug(rec.resume_filename)
					file_data = bytes(rec.resume_content)

					f = open(rec.resume_filename, "wb")
					f.write(file_data)
					f.close()

					(resume_attr_list) = process_single_resume(
						rec.resume_filename)

					_logger.debug(resume_attr_list)
					(retcode, msg, data) = update_resume(
						rec.id, resume_attr_list)

					if (retcode == RetCodes.success.value):
						_logger.info(
							"Resume with id {0} success parsed.".format(rec.id))
					else:
						_logger.warn(
							"Resume with id {0} could not be parsed. Error details are : {1}".format(rec.id, msg))

			except Exception as e:
				_logger.error(e)
				_logger.error(
					'Error occured. Logging it and continue processing next record')

			finally:
				if rec.resume_filename is not None and os.path.exists(rec.resume_filename):
					os.remove(rec.resume_filename)

		return(RetCodes.success.value, "json resumes populated successfully.", None)

	except Exception as dbe:
		_logger.error(dbe)
		return (RetCodes.server_error, str(dbe), None)

	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)



def auto_shortlist_resumes():
	#get resumes created or updated in last xx minutes
	#get tenant ID from recruiter ID who uploaded the resume
	#get JD list for tID
	#auto shortlist if JD primary skill match with resume top skills
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		cursor1 = dbUtils.getNamedTupleCursor(db_con)

		query = """
		SELECT *,json_resume->'top_skills' as top_skills FROM wr_resumes 
		WHERE creation_date >= NOW() - INTERVAL '1 year' AND is_deleted = %s	
		"""

		_logger.debug(cursor.mogrify(query))
		params = (False,)
		cursor.execute(query,params)

		resumeList = cursor.fetchall()
		for resume in resumeList:
			try:
				(retCode,retMsg,tenant) = userUtils.getTenantID(resume.recruiter_id)
				_logger.debug(tenant.tid)

				# (retCode1,retMsg1,jobList) = jdUtils.list_jds_by_tenant(tenant.tid)
				# _logger.debug("Job List for tenant ID is %s ", jobList)

				# for job in jobList:
				#_logger.debug("trying to see if Job ID %s is a match for Resume ID %s", job.id, resume.id)
				skills_list = resume.top_skills 
				if skills_list is not None:
					
					q1 = """select * from wr_jds where 
					recruiter_id in ( select uid from tenant_user_roles where tid = %s)
					and status = %s and is_deleted = %s
					and top_skills && %s"""

					_logger.debug(cursor.mogrify(q1))
					
					params = (tenant.tid,jdUtils.JDStatusCodes.open.value,
								False,list(map(int, skills_list)))
					cursor1.execute(q1,params)
					jobList = cursor1.fetchall()
					print ( jobList)
					for job in jobList:
						try:
							(retCode,retMsg,data) = jdUtils.shortlist(resume.id,job.id,
								datetime.now(tz=timezone.utc), ApplicationStatusCodes.auto_shortlisted.value,
								resume.recruiter_id
							)
							if (retCode != jdUtils.RetCodes.success.value):
								_logger.error("Auto shortlisting failed for job ID %s, resume id %s. Error message is %s", job.id,resume.id, retMsg)

						except Exception as se:
							_logger.error("Auto shortlisting failed for job ID %s, resume id %s", job.id,resume.id)
							_logger.error(se)

			except Exception as dbe:
				_logger.error("Auto shortlisting failed for  resume id %s",resume.id)
				_logger.error(dbe)
			

	except Exception as dbe:
		_logger.error(dbe)
		return (RetCodes.server_error, str(dbe), None)

	finally:
		cursor.close()
		cursor1.close()
		dbUtils.returnToPool(db_con)
	

# main entry point
if __name__ == "__main__":
	#(retCode,msg,data) = save_resume(constants.NEW_ENTITY_ID,None,'rajesh','rkanade@gmail.com','9890303698',1)
	# _logger.debug(retCode)
	# _logger.debug(msg)
	# shortlist(25,[17], datetime.now(tz=timezone.utc),
	#	ApplicationStatusCodes.shortlisted.value,1)

	logging.basicConfig(level = logging.DEBUG)

	#resultData = process_single_resume('C:\\Users\\rajesh\\Downloads\\AK.pdf')
	#print(resultData)

	auto_shortlist_resumes()

	#resultData = process_single_resume('C:\\Users\\rajesh\\Downloads\\Raja_nayak.pdf')

	#logging.basicConfig(level=logging.DEBUG)
	#resultData = search_resumes(1,"Pune")
	#resultData = populate_json_resumes()
