
import dbUtils

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

def save_jd(id,title,details,client, recruiterID,positions=1, open_date=None):
	
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

		if (id == -1):
			##insert a record in user table
			sql = """insert into public.wr_jds ( title, details, client, 
					recruiter_id,positions,status,open_date) 
					values (%s,%s,%s,%s,%s,%s,%s) returning id """
			params = (title,details,client,
					recruiterID,positions,JDStatusCodes.open.value,open_date)

			print ( cursor.mogrify(sql, params))
			
			cursor.execute(sql, params)
			assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

			result = cursor.fetchone()
			jd_id = result[0]
			print ("JD id created is",jd_id )
		

			db_con.commit()
			return (RetCodes.success.value, "JD creation successful.", jd_id)
		else:
			pass

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

def list_jds(recruiterID):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)
		
		query = """SELECT * FROM wr_jds 
				where recruiter_id = %s order by open_date DESC"""
	
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

