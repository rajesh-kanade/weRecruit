import dbUtils
import constants

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
			return (RetCodes.success.value, "Resume creation successful.", resume_id)
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

def list_resumes(recruiterID):
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
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	

## main entry point
if __name__ == "__main__":
	save_resume(constants.NEW_ENTITY_ID,'ddd.pdf','rahul','rahul-email','rahul-phone',1)

