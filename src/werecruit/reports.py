import dbUtils

from enum import Enum

class RetCodes(Enum):
	success = 'JD_CRUD_S200'
	missing_ent_attrs_error = "JD_CRUD_E400"
	empty_ent_attrs_error = "JD_CRUD_E401"
	save_ent_error = "JD_CRUD_E403"
	del_ent_error = "JD_CRUD_E404"
	get_ent_error = "JD_CRUD_E405"
	server_error = "JD_CRUD_E500"

def get_client_wise_summary_report(tenantID):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)

		query = """select client, count(*) from wr_jds 
				where status = 0 and recruiter_id = ( select uid from tenant_user_roles where tid = %s) 
				group by client order by count desc"""

		params = (int(tenantID),)
		print ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		clientSummaryList =cursor.fetchall()

		return(RetCodes.success.value, "Client wise summary report fetched successfully from db for tenant ID {0}".format(tenantID), clientSummaryList)


	except Exception as dbe:
		print(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	

if __name__ == "__main__":

	#(code,msg,resumeList) = get_resumes_not_associated_with_job(18)
	#print (code)
	(code,msg,result) = get_client_wise_summary_report(1)
	print(code)
	print(msg)
	print(result)

