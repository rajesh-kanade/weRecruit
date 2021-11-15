import dbUtils

from enum import Enum

class RetCodes(Enum):
	success = 'RPT_CRUD_S200'
	missing_ent_attrs_error = "RPT_CRUD_E400"
	empty_ent_attrs_error = "RPT_CRUD_E401"
	save_ent_error = "RPT_CRUD_E403"
	del_ent_error = "RPT_CRUD_E404"
	get_ent_error = "RPT_CRUD_E405"
	server_error = "RPT_CRUD_E500"

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


def get_client_wise_job_application_status_summary_report(tenantID):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)

		query = """select client, id, title ,  jd_id, 
					wr_jd_resumes.status , 
					( select description from application_status_codes where id = wr_jd_resumes.status),
					count( wr_jd_resumes.status)
					from wr_jds,wr_jd_resumes
					where wr_jds.id = wr_jd_resumes.jd_id 
					and wr_jds.status = 0
					and wr_jds.id in ( select id from wr_jds where recruiter_id = %s)
					group by id, jd_id,wr_jd_resumes.status
					order by client,wr_jd_resumes.status"""


		params = (int(tenantID),)
		print ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		clientSummaryList =cursor.fetchall()

		return(RetCodes.success.value, "Client wise job application summary report fetched successfully from db for tenant ID {0}".format(tenantID), clientSummaryList)


	except Exception as dbe:
		print(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)


def get_client_wise_revenue_opportunity_report(tenantID):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)

		query = """
			select client,id, title, positions, 
			ctc_currency, 
			sum(((ctc_max*fees_in_percent)/100)*positions) as ro from wr_jds 
			where status = 0  
				and ctc_max is not NULL
				and recruiter_id = ( select uid from tenant_user_roles where tid = %s) group by client ,id
				order by ro asc
			"""

		params = (int(tenantID),)
		print ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		clientSummaryList =cursor.fetchall()

		return(RetCodes.success.value, "Client wise revenue opportunity summary report fetched successfully from db for tenant ID {0}".format(tenantID), clientSummaryList)


	except Exception as dbe:
		print(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)

if __name__ == "__main__":

	#(code,msg,resumeList) = get_resumes_not_associated_with_job(18)
	#print (code)
	(code,msg,result) = get_client_wise_revenue_opportunity_report(1)
	print(code)
	print(msg)
	print(result)

