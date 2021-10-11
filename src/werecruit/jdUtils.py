
import dbUtils

from datetime import datetime
from datetime import timezone 

from enum import Enum
class RetCodes(Enum):
	success = 'JD_CRUD_S200'
	missing_ent_attrs_error = "IAM_CRUD_E400"
	empty_ent_attrs_error = "IAM_CRUD_E401"
	save_ent_error = "IAM_CRUD_E403"
	del_ent_error = "IAM_CRUD_E404"
	get_ent_error = "IAM_CRUD_E405"
	server_error = "IAM_CRUD_E500"
	sign_in_failed = "IAM_CRUD_E411"

class JDStatusCodes(Enum):
	open = 0
	draft = 1
	close = 2


def create_jd(title,details,client, hiring_mgr_name,hiring_mgr_email,recruiterID,positions):
	
	db_con = dbUtils.getConnFromPool()
	cursor = db_con.cursor()
	try:
		
		if not title.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Title field empty or null.", None)

		if not details.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Details field empty or null.", None)

		if not client.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Client field is empty or null.", None)

		if not hiring_mgr_name.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Hiring manager field is empty or null.", None)

		if not hiring_mgr_email.strip():
			 return(RetCodes.empty_ent_attrs_error.value,"Hiring manager email field is empty or null.", None)

		if not recruiterID:
			 return(RetCodes.empty_ent_attrs_error.value,"Recruiter ID field is empty or null.", None)

		if not positions:
			 return(RetCodes.empty_ent_attrs_error.value,"Positions field is empty or null.", None)

		dt = datetime.now(tz=timezone.utc)

		##insert a record in user table
		sql = """insert into public.wr_jds ( title, details, client, 
				hiring_mgr_name, hiring_mgr_emailid, 
				recruiter_id,positions,status,open_date) 
				values (%s,%s, %s,%s,%s,%s,%s,%s,%s) returning id """
		params = (title,details,client,
				hiring_mgr_name, hiring_mgr_email,
				recruiterID,positions,JDStatusCodes.open.value,dt)

		print ( cursor.mogrify(sql, params))
		
		cursor.execute(sql, params)
		assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

		result = cursor.fetchone()
		jd_id = result[0]
		print ("JD id created is",jd_id )
	
		cursor.execute(sql, params)
		assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

		db_con.commit()
		return (RetCodes.success.value, "JD creation successful.", jd_id)


	except Exception as e:
		print(e)
		db_con.rollback()
		return (RetCodes.server_error.value, str(e),None)
	
	finally:
		if cursor is not None:
			cursor.close()
		dbUtils.returnToPool(db_con)

def list_jds(recruiterID):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		
		query = """SELECT * FROM wr_jds 
				where recruiter_id = %s """
	
		params = (recruiterID,)
		print("printing")
		print ( cursor.mogrify(query, params))
		print("post printing")
		cursor.execute(query,params)

		jdList =cursor.fetchall()
		print ( "Total JDs array size ",len(jdList))

		#for jd in jdList:
		#	print(jd)

		return(RetCodes.success.value, "JD List successfully fetched from db", jdList)


	except Exception as dbe:
		print(dbe)
		return ( RetCodes.server_error, str(dbe), None)
		#db_con.rollback()
		#raise
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	


## main entry point
if __name__ == "__main__":

	'''result = create_jd ("T2", "My JD", "NICE",
	'Rajesh Kanade', 'rkanade@gmail.com',1,1)

	print ( result )'''

	result = list_jds(1)
	#print (result)
	jdList = result[2]

	for jd in jdList:
		print (jd.title)

