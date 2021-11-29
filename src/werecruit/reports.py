import dbUtils
import logging

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
		logging.debug ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		clientSummaryList =cursor.fetchall()

		return(RetCodes.success.value, "Client wise summary report fetched successfully from db for tenant ID {0}".format(tenantID), clientSummaryList)


	except Exception as dbe:
		logging.error(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)	


def get_client_wise_job_application_status_summary_report(tenantID):
	try:
		db_con = dbUtils.getConnFromPool()
		cursor = dbUtils.getNamedTupleCursor(db_con)

		query = """
		select id, client, title,
			(jd_stats->'0') as shortlisted,
			(jd_stats->'10') as R1_Interview_Scheduled,
			(jd_stats->'20') as R1_Interview_Cleared,
			(jd_stats->'30') as R1_Interview_Failed,
			(jd_stats->'31') as R1_Interview_No_Show,
			(jd_stats->'40') as R2_Interview_Scheduled,
			(jd_stats->'50') as R2_Interview_Cleared,
			(jd_stats->'60') as R2_Interview_Failed,
			(jd_stats->'61') as R2_Interview_No_Show,
			(jd_stats->'70') as HM_Interview_Scheduled,
			(jd_stats->'80') as HM_Interview_Cleared,
			(jd_stats->'90') as HM_Interview_Failed,
			(jd_stats->'91') as HM_Interview_No_Show,
			(jd_stats->'100') as HR_Interview_Scheduled,
			(jd_stats->'110') as HR_Interview_Cleared,
			(jd_stats->'120') as HR_Interview_Failed,
			(jd_stats->'121') as HR_Interview_No_Show,
			(jd_stats->'130') as Offer_Pending,
			(jd_stats->'140') as Offer_Released,
			(jd_stats->'150') as Offer_Accepted,
			(jd_stats->'160') as Joined,
			(jd_stats->'170') as No_show
			from wr_jds 
			where status = 0
			and recruiter_id in ( select uid from tenant_user_roles where tid = %s)
			order by client, id
		"""


		params = (int(tenantID),)
		logging.debug ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		clientSummaryList =cursor.fetchall()

		return(RetCodes.success.value, "Client wise job application summary report fetched successfully from db for tenant ID {0}".format(tenantID), clientSummaryList)


	except Exception as dbe:
		logging.error(dbe)
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
		logging.debug ( cursor.mogrify(query, params))
		cursor.execute(query,params)

		clientSummaryList =cursor.fetchall()

		return(RetCodes.success.value, "Client wise revenue opportunity summary report fetched successfully from db for tenant ID {0}".format(tenantID), clientSummaryList)


	except Exception as dbe:
		logging.error(dbe)
		return ( RetCodes.server_error, str(dbe), None)
	
	finally:
		cursor.close()
		dbUtils.returnToPool(db_con)

if __name__ == "__main__":

	#(code,msg,resumeList) = get_resumes_not_associated_with_job(18)
	#logging.debug (code)
	(code,msg,result) = get_client_wise_revenue_opportunity_report(1)
	logging.debug(code)
	logging.debug(msg)
	logging.debug(result)

