import dbUtils
import constants

from datetime import datetime
from datetime import timezone

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
	print('inside save_resume function')
	db_con = dbUtils.getConnFromPool()
	cursor = db_con.cursor()
	try:
		
		if not candidateName.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Candidate Name empty or null.", None)

		if not candidateEmail.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Candidate Email empty or null.", None)

		if not candidatePhone.strip():
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

			print ( cursor.mogrify(sql, params))
			
			cursor.execute(sql, params)
			assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

			result = cursor.fetchone()
			resume_id = result[0]
			print ("Resume id {} successfully created.".format(resume_id))

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
						
			print ( cursor.mogrify(sql, params))
			
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
				
			print ("Resume id {0} updated successfully.".format(id) )
		
			db_con.commit()
			return (RetCodes.success.value, "Resume id {0} updated successfully.".format(id),id)
			
	except Exception as e:
		print(e)
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
		print ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		resumeList =cursor.fetchall()

		return(RetCodes.success.value, "Resume List successfully fetched from db", resumeList)


	except Exception as dbe:
		print(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	

def list_resumes_by_tenant(tenantID):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		
		query = """SELECT * FROM wr_resumes 
				where recruiter_id = ( select uid from tenant_user_roles where tid = %s) 
				order by id desc"""
	
		params = (tenantID,)
		print ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		resumeList =cursor.fetchall()

		return(RetCodes.success.value, "Resume List successfully fetched from db for tenant ID {0}".format(tenantID), resumeList)

	except Exception as dbe:
		print(dbe)
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
		print ( cursor.mogrify(query, ))
		cursor.execute(query,)

		appStatusCodesList =cursor.fetchall()

		return(RetCodes.success.value, "Application status code List successfully fetched from db", appStatusCodesList)


	except Exception as dbe:
		print(dbe)
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
		print ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		assert cursor.rowcount == 1, "assertion failed : Effected row count is not equal to 1."

		resume = cursor.fetchone()

		return(RetCodes.success.value, "Resume  for id {0} successfully fetched from db".format(id), resume)


	except Exception as dbe:
		print(dbe)
		return ( RetCodes.server_error.value, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	




## main entry point
if __name__ == "__main__":
	save_resume(constants.NEW_ENTITY_ID,'ddd.pdf','rahul','rahul-email','rahul-phone',1)
	#shortlist(25,[17], datetime.now(tz=timezone.utc),
	#	ApplicationStatusCodes.shortlisted.value,1)

