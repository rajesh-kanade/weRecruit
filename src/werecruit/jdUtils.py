
import dbUtils
import constants

from datetime import datetime
from datetime import timezone 

from enum import Enum
class RetCodes(Enum):
	success = 'JD_CRUD_S200'
	missing_ent_attrs_error = "JD_CRUD_E400"
	empty_ent_attrs_error = "JD_CRUD_E401"
	save_ent_error = "JD_CRUD_E403"
	del_ent_error = "JD_CRUD_E404"
	get_ent_error = "JD_CRUD_E405"
	server_error = "JD_CRUD_E500"

class JDStatusCodes(Enum):
	open = 0
	draft = 1
	close = 2

JD_DEF_POSITIONS = 1

def save_jd(id,title,details,client, recruiterID,positions=JD_DEF_POSITIONS, open_date=None,
			ip_name1=None, ip_email1=None,ip_phone1=None,
			ip_name2=None, ip_email2=None,ip_phone2=None,
			hiring_mgr_name= None, hiring_mgr_email=None,hiring_mgr_phone=None,
			hr_name= None, hr_email=None,hr_phone=None,
			status=JDStatusCodes.open.value ):
	
	print('inside save_jd function')
	db_con = dbUtils.getConnFromPool()
	cursor = db_con.cursor()
	try:
		
		if not title.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Title field empty or null.", None)

		if not details.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Details field empty or null.", None)

		if not client.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Client field is empty or null.", None)

		if not recruiterID:
			 return(RetCodes.empty_ent_attrs_error.value,"Recruiter ID field is empty or null.", None)

		if not positions:
			 return(RetCodes.empty_ent_attrs_error.value,"Positions field is empty or null.", None)

		if open_date is None:
			open_date = datetime.now(tz=timezone.utc)

		if (int(id) == constants.NEW_ENTITY_ID):
			##insert a record in user table
			sql = """insert into public.wr_jds ( title, details, client, 
					recruiter_id,positions,status,open_date,
					ip_name_1, ip_emailid_1,ip_phone_1,
					ip_name_2, ip_emailid_2,ip_phone_2,
					hiring_mgr_name, hiring_mgr_emailid,hiring_mgr_phone,
					hr_name,hr_emailid,hr_phone ) 
					values (%s,%s,%s,
					%s,%s,%s,%s,
					%s,%s,%s,
					%s,%s,%s,
					%s,%s,%s,
					%s,%s,%s) returning id """
			
			params = (title,details,client,
					recruiterID,int(positions),int(status),open_date,
					ip_name1,ip_email1,ip_phone1,
					ip_name2,ip_email2,ip_phone2,
					hiring_mgr_name,hiring_mgr_email,hiring_mgr_phone,
					hr_name,hr_email,hr_phone)

			print ( cursor.mogrify(sql, params))
			
			cursor.execute(sql, params)
			assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

			result = cursor.fetchone()
			jd_id = result[0]
			print ("JD id created is",jd_id )
		

			db_con.commit()
			return (RetCodes.success.value, "JD creation successful.", jd_id)
		else:
			sql = """update public.wr_jds set  
						title = %s,  details = %s,  client = %s,
						recruiter_id = %s, positions = %s, status =%s, open_date= %s ,
						ip_name_1 = %s, ip_emailid_1 = %s, ip_phone_1 = %s,
						ip_name_2 = %s, ip_emailid_2 = %s, ip_phone_2 = %s,
						hiring_mgr_name = %s, hiring_mgr_emailid = %s, hiring_mgr_phone = %s,
						hr_name = %s, hr_emailid = %s, hr_phone = %s
					where id = %s"""
			params = (title,details,client, 
						recruiterID, int(positions), int(status), open_date,
						ip_name1,ip_email1,ip_phone1,
						ip_name2,ip_email2,ip_phone2,
						hiring_mgr_name, hiring_mgr_email,hiring_mgr_phone,
						hr_name, hr_email,hr_phone,
						int(id))
						
			print ( cursor.mogrify(sql, params))
			
			cursor.execute(sql, params)
			assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

			#result = cursor.fetchone()
			#jd_id = result[0]
			print ("JD id {0} updated successfully.".format(id) )
		
			db_con.commit()
			return (RetCodes.success.value, "JD {0} updated successfully.".format(id),id)
			

	except Exception as e:
		print(e)
		db_con.rollback()
		return (RetCodes.server_error.value, str(e),None)
	
	finally:
		if cursor is not None:
			cursor.close()
		dbUtils.returnToPool(db_con)

def save_header(id, title,details,client):
	
	db_con = dbUtils.getConnFromPool()
	cursor = db_con.cursor()
	try:
		
		if not title.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Title field empty or null.", None)

		if not details.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Details field empty or null.", None)

		if not client.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Client field is empty or null.", None)


		dt = datetime.now(tz=timezone.utc)

		##insert a record in user table
		sql = """update public.wr_jds set title = %s,  details = %s,  
				client = %s where id = %s"""
		params = (title,details,client, int(id))


		print ( cursor.mogrify(sql, params))
		
		cursor.execute(sql, params)
		print(cursor.rowcount)
		assert cursor.rowcount == 1, "assertion failed : {0} Rows returned which is not equal to 1.".format(cursor.rowcount)

		#result = cursor.fetchone()

		db_con.commit()
		return (RetCodes.success.value, "JD updated successful.", None)


	except Exception as e:
		print(e)
		db_con.rollback()
		return (RetCodes.server_error.value, str(e),None)
	
	finally:
		if cursor is not None:
			cursor.close()
		dbUtils.returnToPool(db_con)

def list_jds(recruiterID, statusFilter = None):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		
		query = """SELECT * FROM wr_jds 
				where recruiter_id = %s 
				order by open_date DESC"""
	
		params = (recruiterID,)
		print ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		jdList =cursor.fetchall()

		return(RetCodes.success.value, "JD List successfully fetched from db", jdList)


	except Exception as dbe:
		print(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	

def get(id):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		
		query = """SELECT * FROM wr_jds 
				where id = %s"""
	
		params = (id,)
		print ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

		jd = cursor.fetchone()

		return(RetCodes.success.value, "JD  info for {0} successfully fetched from db".format(id), jd)


	except Exception as dbe:
		print(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	

def get_resumes_associated_with_job(job_id):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		
		#query = """select * from wr_resumes 
		#			where id in ( select resume_id from wr_jd_resumes where jd_id = %s)"""
		query = """select wr_resumes.*,wr_jd_resumes.status from wr_resumes ,wr_jd_resumes
					where wr_resumes.id = wr_jd_resumes.resume_id
					and wr_jd_resumes.jd_id = %s """

		params = (int(job_id),)
		print ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		resumeList = cursor.fetchall()

		return(RetCodes.success.value, "Resumes associated with job JD {0}  fetched successfully.".format(job_id), resumeList)

	except Exception as dbe:
		print(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	


# This function returns all the resume records that are not currently 
# associated with a particular job id
def get_resumes_not_associated_with_job(job_id):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		
		query = """select *
					from wr_resumes where id not in 
					( select resume_id from wr_jd_resumes where jd_id = %s)"""

		params = (int(job_id),)
		print ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		resumeList = cursor.fetchall()

		return(RetCodes.success.value, "Resumes not associated with job JD {0}  fetched successfully.".format(job_id), resumeList)

	except Exception as dbe:
		print(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	

# This inserts status and notes for a given job application ( job ID + resume ID)
def insert_job_application_status(job_id, resume_id,change_date,changed_by,status, notes):
	
	try:

		db_con = dbUtils.getConnFromPool()
		cursor = db_con.cursor()

		sql = """insert into public.wr_jd_resume_status_audit_log ( jd_id,resume_id,
			change_date, changed_by,status,notes ) 
			values (%s,%s,
			%s, %s, %s,%s)"""
	
		params = (int(job_id), int(resume_id),
				change_date,int(changed_by),int(status),notes)

		print (cursor.mogrify(sql, params))
	
		cursor.execute(sql, params)
		assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

		#now update the wr_jd_resumes table with this latest status and notes
		sql = """update wr_jd_resumes set status = %s, notes = %s 
				where jd_id = %s and resume_id = %s"""
		params = ( int(status),notes,job_id,resume_id)
		cursor.execute(sql, params)
		assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

		#result = cursor.fetchone()
	
		db_con.commit()
		
		return (RetCodes.success.value, "Application status updated successful.", None)
			
	except Exception as e:
		print(e)
		db_con.rollback()
		return (RetCodes.server_error.value, str(e),None)
	
	finally:
		if cursor is not None:
			cursor.close()
		dbUtils.returnToPool(db_con)
# we may not need this function at all ....
def shortlist(resume_id,jd_id, application_date,status,recruiterid):
	print('inside shortlist function')
	db_con = dbUtils.getConnFromPool()
	cursor = db_con.cursor()
	try:

		sql = """insert into public.wr_jd_resumes ( resume_id,jd_id, 
			application_date, status ) 
			values (%s,%s,
			%s, %s)"""
	
		params = (int(resume_id),int(jd_id),application_date,int(status))

		print ( cursor.mogrify(sql, params))
	
		cursor.execute(sql, params)
		assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."			
		#result = cursor.fetchone()
		db_con.commit()

		#Now insert into application status table also as the first record
		# TODO can both be part of same transaction to save 1 query but more then that
		# have data consistency		
		insert_job_application_status(jd_id,resume_id,
			application_date,recruiterid, status, "")

		return (RetCodes.success.value, "Resume creation successful.", None)
			
	except Exception as e:
		print(e)
		db_con.rollback()
		return (RetCodes.server_error.value, str(e),None)
	
	finally:
		if cursor is not None:
			cursor.close()
		dbUtils.returnToPool(db_con)

def save_resume_to_job(job_id, resume_id, resumeFileName, candidateName, candidateEmail, candidatePhone):
	
	print('inside save_jd function')
	db_con = dbUtils.getConnFromPool()
	cursor = db_con.cursor()
	try:
		
		if not candidateName.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Title field empty or null.", None)

		if not candidateEmail.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Details field empty or null.", None)

		if not candidatePhone.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Client field is empty or null.", None)

		if not recruiterID:
			 return(RetCodes.empty_ent_attrs_error.value,"Recruiter ID field is empty or null.", None)

		if not positions:
			 return(RetCodes.empty_ent_attrs_error.value,"Positions field is empty or null.", None)

		if open_date is None:
			open_date = datetime.now(tz=timezone.utc)

		if (int(id) == constants.NEW_ENTITY_ID):
			##insert a record in user table
			sql = """insert into public.wr_jds ( title, details, client, 
					recruiter_id,positions,status,open_date,
					ip_name_1, ip_emailid_1,ip_phone_1,
					ip_name_2, ip_emailid_2,ip_phone_2,
					hiring_mgr_name, hiring_mgr_emailid,hiring_mgr_phone,
					hr_name,hr_emailid,hr_phone ) 
					values (%s,%s,%s,
					%s,%s,%s,%s,
					%s,%s,%s,
					%s,%s,%s,
					%s,%s,%s,
					%s,%s,%s) returning id """
			
			params = (title,details,client,
					recruiterID,int(positions),int(status),open_date,
					ip_name1,ip_email1,ip_phone1,
					ip_name2,ip_email2,ip_phone2,
					hiring_mgr_name,hiring_mgr_email,hiring_mgr_phone,
					hr_name,hr_email,hr_phone)

			print ( cursor.mogrify(sql, params))
			
			cursor.execute(sql, params)
			assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

			result = cursor.fetchone()
			jd_id = result[0]
			print ("JD id created is",jd_id )
		

			db_con.commit()
			return (RetCodes.success.value, "JD creation successful.", jd_id)
		else:
			sql = """update public.wr_jds set  
						title = %s,  details = %s,  client = %s,
						recruiter_id = %s, positions = %s, status =%s, open_date= %s ,
						ip_name_1 = %s, ip_emailid_1 = %s, ip_phone_1 = %s,
						ip_name_2 = %s, ip_emailid_2 = %s, ip_phone_2 = %s,
						hiring_mgr_name = %s, hiring_mgr_emailid = %s, hiring_mgr_phone = %s,
						hr_name = %s, hr_emailid = %s, hr_phone = %s
					where id = %s"""
			params = (title,details,client, 
						recruiterID, int(positions), int(status), open_date,
						ip_name1,ip_email1,ip_phone1,
						ip_name2,ip_email2,ip_phone2,
						hiring_mgr_name, hiring_mgr_email,hiring_mgr_phone,
						hr_name, hr_email,hr_phone,
						int(id))
						
			print ( cursor.mogrify(sql, params))
			
			cursor.execute(sql, params)
			assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

			#result = cursor.fetchone()
			#jd_id = result[0]
			print ("JD id {0} updated successfully.".format(id) )
		
			db_con.commit()
			return (RetCodes.success.value, "JD {0} updated successfully.".format(id),id)
			

	except Exception as e:
		print(e)
		db_con.rollback()
		return (RetCodes.server_error.value, str(e),None)
	
	finally:
		if cursor is not None:
			cursor.close()
		dbUtils.returnToPool(db_con)



## main entry point
if __name__ == "__main__":

	#(code,msg,resumeList) = get_resumes_not_associated_with_job(18)
	#print (code)
	dt = datetime.now(tz=timezone.utc)
	(code,msg,result) = insert_job_application_status( 1,1,dt,1,10,"Testing status update")
	print(code)
	print(msg)



