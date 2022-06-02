
from datetime import timezone
from enum import Enum
from datetime import datetime
import json
import dbUtils
import constants
import resumeUtils

import decimal
from commonUtils import getFileExtension
#from dotenv import load_dotenv , find_dotenv
import logging
_logger = logging.getLogger()
# load_dotenv(find_dotenv())


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


def save_jd(id, title, details, client, recruiterID, positions=JD_DEF_POSITIONS, open_date=None,
            ip_name1=None, ip_email1=None, ip_phone1=None,
            ip_name2=None, ip_email2=None, ip_phone2=None,
            hiring_mgr_name=None, hiring_mgr_email=None, hiring_mgr_phone=None,
            hr_name=None, hr_email=None, hr_phone=None,
            status=JDStatusCodes.open.value,
            city_id=None, min_yrs_of_exp=None, jd_file_name=None,
            primary_skills=None, secondary_skills=None,
            ctc_min=None, ctc_max=None, ctc_currency=None,
            fees_percent=None, warranty_period_in_months=None,
            max_yrs_of_exp=None):

    _logger.debug('inside save_jd function')
    db_con = dbUtils.getConnFromPool()
    cursor = db_con.cursor()
    try:

        if not title.strip():
            return(RetCodes.empty_ent_attrs_error.value, "Title field empty or null.", None)

        # if not details.strip():
        #	 return(RetCodes.empty_ent_attrs_error.value,"Details field empty or null.", None)

        if not client.strip():
            return(RetCodes.empty_ent_attrs_error.value, "Client field is empty or null.", None)

        if not recruiterID:
            return(RetCodes.empty_ent_attrs_error.value, "Recruiter ID field is empty or null.", None)

        if (max_yrs_of_exp is not None and min_yrs_of_exp is not None):
            if (max_yrs_of_exp < min_yrs_of_exp):
                return(RetCodes.save_ent_error.value, "Maximum years of experience can not be less then minimum years of experience .", None)

        if (ctc_max is not None and ctc_min is not None):
            if (ctc_max < ctc_min):
                return(RetCodes.save_ent_error.value, "Maximum CTC can not be less then minimum CTC .", None)

        if open_date is None:
            open_date = datetime.now(tz=timezone.utc)

        _logger.debug('Client JD file name is {0}'.format(jd_file_name))
        
        ext = getFileExtension(jd_file_name)
        if ext not in ['docx','pdf']:
            raise Exception('unsupported jd file type {0}'.format(ext))
        if (jd_file_name is None):
            file_data = None
        else:
            file_data = bytes(open(jd_file_name, "rb").read())

        if (int(id) == constants.NEW_ENTITY_ID):
            # insert a record in user table
            _logger.debug('creating new JD with id %s ', id)

            sql = """insert into public.wr_jds ( title, details, client, 
					recruiter_id,positions,status,open_date,
					ip_name_1, ip_emailid_1,ip_phone_1,
					ip_name_2, ip_emailid_2,ip_phone_2,
					hiring_mgr_name, hiring_mgr_emailid,hiring_mgr_phone,
					hr_name,hr_emailid,hr_phone,
					city_id,min_yrs_of_exp,jd_file_name,
					primary_skills, secondary_skills,
					ctc_min,ctc_max,ctc_currency ,
					fees_in_percent,warranty_period_in_months,client_jd,max_yrs_of_exp) 
					values (%s,%s,%s,
					%s,%s,%s,%s,
					%s,%s,%s,
					%s,%s,%s,
					%s,%s,%s,
					%s,%s,%s,
				    %s,%s,%s,
					%s,%s,
					%s,%s,%s,
					%s,%s,%s,%s) returning id """

            params = (title, details, client,
                      recruiterID, int(positions), int(status), open_date,
                      ip_name1, ip_email1, ip_phone1,
                      ip_name2, ip_email2, ip_phone2,
                      hiring_mgr_name, hiring_mgr_email, hiring_mgr_phone,
                      hr_name, hr_email, hr_phone,
                      city_id, min_yrs_of_exp, jd_file_name,
                      primary_skills, secondary_skills,
                      ctc_min, ctc_max, ctc_currency,
                      fees_percent, warranty_period_in_months,
                      file_data, max_yrs_of_exp)

            _logger.debug(cursor.mogrify(sql, params))

            cursor.execute(sql, params)
            assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

            result = cursor.fetchone()
            jd_id = result[0]
            _logger.debug("JD id{0} successfully created.".format(jd_id))

            db_con.commit()
            return (RetCodes.success.value, "JD creation successful.", jd_id)
        else:
            _logger.debug(
                "inside save_jd update. jd file path is : ".format(jd_file_name))
            sql = """update public.wr_jds set  
						title = %s,  details = %s,  client = %s,
						recruiter_id = %s, positions = %s, status =%s,
						ip_name_1 = %s, ip_emailid_1 = %s, ip_phone_1 = %s,
						ip_name_2 = %s, ip_emailid_2 = %s, ip_phone_2 = %s,
						hiring_mgr_name = %s, hiring_mgr_emailid = %s, hiring_mgr_phone = %s,
						hr_name = %s, hr_emailid = %s, hr_phone = %s,
						city_id=%s,min_yrs_of_exp =%s,
						primary_skills=%s,secondary_skills=%s,
						ctc_min=%s,ctc_max=%s,ctc_currency=%s,
						fees_in_percent=%s,warranty_period_in_months=%s,max_yrs_of_exp=%s
					where id = %s"""
            params = (title, details, client,
                      recruiterID, int(positions), int(status),
                      ip_name1, ip_email1, ip_phone1,
                      ip_name2, ip_email2, ip_phone2,
                      hiring_mgr_name, hiring_mgr_email, hiring_mgr_phone,
                      hr_name, hr_email, hr_phone,
                      city_id, min_yrs_of_exp,
                      primary_skills, secondary_skills,
                      ctc_min, ctc_max, ctc_currency,
                      fees_percent, warranty_period_in_months, max_yrs_of_exp,
                      int(id))

            _logger.debug(cursor.mogrify(sql, params))

            cursor.execute(sql, params)
            assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

            # This is bad code as unnecessary second db call is being made, need to be refactored
            if (jd_file_name != None):
                _logger.debug(
                    'JD file name is not null so updating the file name and content for job id {0}'.format(id))
                sql1 = """update public.wr_jds set  
						jd_file_name = %s,
						client_jd = %s
						where id = %s
					"""
                params1 = (jd_file_name, file_data, id)
                cursor.execute(sql1, params1)
                assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

            db_con.commit()
            _logger.debug("JD id {0} updated successfully.".format(id))

            return (RetCodes.success.value, "JD {0} updated successfully.".format(id), id)

    except Exception as e:
        _logger.error(e)
        db_con.rollback()
        return (RetCodes.server_error.value, str(e), None)

    finally:
        if cursor is not None:
            cursor.close()
        dbUtils.returnToPool(db_con)


def save_header(id, title, details, client):

    db_con = dbUtils.getConnFromPool()
    cursor = db_con.cursor()
    try:

        if not title.strip():
            return(RetCodes.empty_ent_attrs_error.value, "Title field empty or null.", None)

        if not details.strip():
            return(RetCodes.empty_ent_attrs_error.value, "Details field empty or null.", None)

        if not client.strip():
            return(RetCodes.empty_ent_attrs_error.value, "Client field is empty or null.", None)

        dt = datetime.now(tz=timezone.utc)

        # insert a record in user table
        sql = """update public.wr_jds set title = %s,  details = %s,  
				client = %s where id = %s"""
        params = (title, details, client, int(id))

        _logger.debug(cursor.mogrify(sql, params))

        cursor.execute(sql, params)
        _logger.debug(cursor.rowcount)
        assert cursor.rowcount == 1, "assertion failed : {0} Rows returned which is not equal to 1.".format(
            cursor.rowcount)

        #result = cursor.fetchone()

        db_con.commit()
        return (RetCodes.success.value, "JD updated successful.", None)

    except Exception as e:
        _logger.error(e)
        db_con.rollback()
        return (RetCodes.server_error.value, str(e), None)

    finally:
        if cursor is not None:
            cursor.close()
        dbUtils.returnToPool(db_con)


def list_jds_by_tenant(tenantID, orderBy=None, order=None, statusFilter=None, limit=1000):
    try:
        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        query, params = None, None

        if not orderBy:
            query = """SELECT * FROM wr_jds 
                        where is_deleted = False and 
                        recruiter_id in ( select uid from tenant_user_roles where tid = %s)
                        order by id DESC limit %s"""
        elif orderBy == 'client':
            query = """SELECT * FROM wr_jds 
                        where is_deleted = False and 
                        recruiter_id in ( select uid from tenant_user_roles where tid = %s)
                        order by client, id DESC limit %s"""

        elif orderBy == 'status':
            query = """SELECT * FROM wr_jds 
                        where is_deleted = False and 
                        recruiter_id in ( select uid from tenant_user_roles where tid = %s)
                        order by status, id DESC limit %s"""

        elif orderBy == 'title':
            query = """SELECT * FROM wr_jds 
                        where is_deleted = False and 
                        recruiter_id in ( select uid from tenant_user_roles where tid = %s)
                        order by title, id DESC limit %s"""
        elif orderBy == 'open_date':
            query = """SELECT * FROM wr_jds 
                        where is_deleted = False and 
                        recruiter_id in ( select uid from tenant_user_roles where tid = %s)
                        order by open_date, id DESC limit %s"""
        else:
            query = """SELECT * FROM wr_jds 
                        where is_deleted = False and 
                        recruiter_id in ( select uid from tenant_user_roles where tid = %s)
                        order by hiring_mgr_name, id DESC limit %s"""

        params = (tenantID, limit)

        _logger.debug(cursor.mogrify(query, params))
        # print(cursor.mogrify(query, params))
        cursor.execute(query, params)

        jdList = cursor.fetchall()

        if order == 'DESC':
            jdList = jdList[::-1]
        # print(jdList)
        return(RetCodes.success.value, "JD List successfully fetched from db for tenant ID".format(tenantID), jdList)

    except Exception as dbe:
        _logger.error(dbe)
        return (RetCodes.server_error, str(dbe), None)

    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)


def get(id):
    try:
        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        query = """SELECT *
				FROM wr_jds 
				where id = %s and is_deleted = %s"""

        params = (id, False)
        _logger.debug(cursor.mogrify(query, params))
        cursor.execute(query, params)

        assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

        jd = cursor.fetchone()

        return(RetCodes.success.value, "JD  info for {0} successfully fetched from db".format(id), jd)

    except Exception as dbe:
        _logger.error(dbe)
        return (RetCodes.server_error, str(dbe), None)

    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)


def get_resumes_associated_with_job(job_id, cat_status_code=None,sub_cat_status_code=None):
    try:
        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        # query = """select * from wr_resumes
        #			where id in ( select resume_id from wr_jd_resumes where jd_id = %s)"""
        query = """select wr_resumes.*,wr_jd_resumes.status ,
					(select description from application_status_codes where id = status)
					from wr_resumes ,wr_jd_resumes
					where wr_resumes.id = wr_jd_resumes.resume_id
					and wr_jd_resumes.jd_id = %s """
        
        catStatusCodeQuery = """and wr_jd_resumes.status in
                                (select id from resume_application_status_codes_sub_category
                                    WHERE category_id = %s
					                ORDER BY id ASC
                                )"""
        subCatstatusCodeQuery = """and wr_jd_resumes.status = %s"""
        params = (int(job_id),)
        if cat_status_code is not None:
            query += catStatusCodeQuery
            params = (int(job_id), cat_status_code)
        elif sub_cat_status_code is not None:
            query += subCatstatusCodeQuery
            params = (int(job_id), sub_cat_status_code)

        _logger.debug(cursor.mogrify(query, params))
        cursor.execute(query, params)

        resumeList = cursor.fetchall()

        return(RetCodes.success.value, "Resumes associated with job JD {0}  fetched successfully.".format(job_id), resumeList)

    except Exception as dbe:
        _logger.error(dbe)
        return (RetCodes.server_error, str(dbe), None)

    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)


# This function returns all the resume records that are not currently
# associated with a particular job id
def get_resumes_not_associated_with_job(job_id, ftsearch, tenant_id):
    try:
        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        query = """select *
					from wr_resumes where id not in 
					( select resume_id from wr_jd_resumes where jd_id = %s)
					and recruiter_id in 
					( select uid from tenant_user_roles where tid = %s)
				"""

        if bool(ftsearch):
            kwrdList = ftsearch.split()
            _logger.debug(
                "Keyword list for free text is as under %s", kwrdList)
            ft_cond = ' AND '.join(
                "to_tsvector('english',json_resume) @@ to_tsquery('{0}')".format(word) for word in kwrdList)
            query = query + " and " + ft_cond

        query = query + " order by id desc "

        params = (int(job_id), int(tenant_id))
        _logger.debug(cursor.mogrify(query, params))
        cursor.execute(query, params)

        resumeList = cursor.fetchall()

        return(RetCodes.success.value, "Resumes not associated with job JD {0}  fetched successfully.".format(job_id), resumeList)

    except Exception as dbe:
        _logger.error(dbe)
        return (RetCodes.server_error, str(dbe), None)

    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)

# This inserts status and notes for a given job application ( job ID + resume ID)


def insert_job_application_status(job_id, resume_id, change_date, changed_by, status, notes):

    try:

        db_con = dbUtils.getConnFromPool()
        cursor = db_con.cursor()

        sql = """insert into public.wr_jd_resume_status_audit_log ( jd_id,resume_id,
			change_date, changed_by,status,notes ) 
			values (%s,%s,
			%s, %s, %s,%s)"""

        params = (int(job_id), int(resume_id),
                  change_date, int(changed_by), int(status), notes)

        _logger.debug(cursor.mogrify(sql, params))

        cursor.execute(sql, params)
        assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

        # now update the wr_jd_resumes table with this latest status and notes
        sql = """update wr_jd_resumes set status = %s, notes = %s 
				where jd_id = %s and resume_id = %s"""
        params = (int(status), notes, job_id, resume_id)
        cursor.execute(sql, params)
        assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."

        #result = cursor.fetchone()

        db_con.commit()

        return (RetCodes.success.value, "Application status updated successful.", None)

    except Exception as e:
        _logger.error(e)
        db_con.rollback()
        return (RetCodes.server_error.value, str(e), None)

    finally:
        if cursor is not None:
            cursor.close()
        dbUtils.returnToPool(db_con)

# we may not need this function at all ....


def shortlist(resume_id, jd_id, application_date, status, recruiterid):
    _logger.debug('inside shortlist function')
    db_con = dbUtils.getConnFromPool()
    cursor = db_con.cursor()
    try:

        sql = """insert into public.wr_jd_resumes ( resume_id,jd_id, 
			application_date, status ) 
			values (%s,%s,
			%s, %s)"""

        params = (int(resume_id), int(jd_id), application_date, int(status))

        _logger.debug(cursor.mogrify(sql, params))

        cursor.execute(sql, params)
        assert cursor.rowcount == 1, "assertion failed : Row Effected is not equal to 1."
        #result = cursor.fetchone()
        db_con.commit()

        # Now insert into application status table also as the first record
        # TODO can both be part of same transaction to save 1 query but more then that
        # have data consistency
        insert_job_application_status(jd_id, resume_id,
                                      application_date, recruiterid, status, "")

        return (RetCodes.success.value, "Resume creation successful.", None)

    except Exception as e:
        _logger.error(e)
        db_con.rollback()
        return (RetCodes.server_error.value, str(e), None)

    finally:
        if cursor is not None:
            cursor.close()
        dbUtils.returnToPool(db_con)


def get_job_status_summary(job_id):

    try:
        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        query = """select status, 
					( select description from application_status_codes where id = status) ,
					count(status) 
					from wr_jd_resumes 
					where jd_id IN ( select id from wr_jds 
						where id =%s )
						group by status;
				"""

        params = (int(job_id),)
        _logger.debug(cursor.mogrify(query, params))
        cursor.execute(query, params)

        jobStatusSummaryList = cursor.fetchall()

        return(RetCodes.success.value, "Status summary  for job JD {0}  fetched successfully.".format(job_id), jobStatusSummaryList)

    except Exception as dbe:
        _logger.error(dbe)
        return (RetCodes.server_error, str(dbe), None)

    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)


def update_job_stats():
    # get all active jobs across tenants
    # get stats for each such job and keep them in job stats column
    try:
        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        #assert False,"Hardcoded fail"

        query = """SELECT * FROM wr_jds 
				where status = %s"""

        params = (JDStatusCodes.open.value,)
        _logger.debug(cursor.mogrify(query, params))
        #_logger.debug ( cursor.mogrify(query, params))
        cursor.execute(query, params)

        jdList = cursor.fetchall()

        (retCode, msg, appStatusCodes) = resumeUtils.list_application_status_codes()
        assert retCode == resumeUtils.RetCodes.success.value, "Failed to fetch application status codes."

        for job in jdList:
            #print (job.id)
            jdstats = {}

            cursor1 = dbUtils.getNamedTupleCursor(db_con)

            for code in appStatusCodes:
                #print (code.id)
                query = """SELECT count(status) FROM wr_jd_resumes
					where status = %s and jd_id = %s"""
                #params = ( code.id, job.id)
                params = (code.id, job.id)
                _logger.debug(cursor.mogrify(query, params))
                cursor1.execute(query, params)
                data = cursor1.fetchone()
                jdstats[code.id] = data.count
                # cursor.close()
                # cursor.clear()

            # cursor1.close()
            # print(jdstats)

            cursor2 = dbUtils.getNamedTupleCursor(db_con)

            query = """UPDATE wr_jds set jd_stats =%s where id = %s"""
            jdstats_json = json.dumps(jdstats, indent=4, sort_keys=False)

            params = (str(jdstats_json), job.id)
            _logger.debug(cursor.mogrify(query, params))
            cursor2.execute(query, params)
            # cursor.commit()
            db_con.commit()
            # cursor2.close()

    except Exception as dbe:
        _logger.error(dbe)
        db_con.rollback()
        return (RetCodes.server_error, str(dbe), None)

    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'cursor1' in locals() and cursor1 is not None:
            cursor1.close()
        if 'cursor2' in locals() and cursor2 is not None:
            cursor2.close()

        # if db_con in locals() and db_con is not None:
        dbUtils.returnToPool(db_con)

def get_country_names():
    try:
        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        query = """SELECT *
				FROM countries
				ORDER BY id"""

        params = ()
        _logger.debug(cursor.mogrify(query, params))
        cursor.execute(query, params)

        country_names = cursor.fetchall()

        return(RetCodes.success.value, "Country names successfully fetched from database", country_names)

    except Exception as dbe:
        _logger.error(dbe)
        return (RetCodes.server_error, str(dbe), None)

    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)
        

def get_city_names(country_id):
    try:
        db_con = dbUtils.getConnFromPool()
        cursor = dbUtils.getNamedTupleCursor(db_con)

        query = """SELECT *
				FROM cities
                WHERE country_id = %s
				ORDER BY id ASC LIMIT 50
                """

        params = (country_id,)
        _logger.debug(cursor.mogrify(query, params))
        cursor.execute(query, params)

        city_names = cursor.fetchall()

        return(RetCodes.success.value, "Country names successfully fetched from database", city_names)

    except Exception as dbe:
        _logger.error(dbe)
        return (RetCodes.server_error, str(dbe), None)

    finally:
        cursor.close()
        dbUtils.returnToPool(db_con)
# main entry point
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    (code, msg, resumeList) = get_resumes_not_associated_with_job(40, 'pune', 1)
    _logger.debug(code)
    _logger.debug(msg)
    _logger.debug('Total resumes found is %s', len(resumeList))
    #_logger.debug( resumeList)

    # logging.basicConfig(level=logging.DEBUG)

    '''dt = datetime.now(tz=timezone.utc)
	(code,msg,result) = get_job_status_summary(18)
	_logger.debug(code)
	_logger.debug(msg)
	_logger.debug(result)'''

    # update_job_stats()
    #(code,msg,resumeList) = save_jd(-1,"test for attachment",'','testclient')
