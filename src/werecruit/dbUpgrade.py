from dotenv import load_dotenv, find_dotenv
import dbUtils
from enum import Enum
import logging
_logger = logging.getLogger()

load_dotenv(find_dotenv())

class RetCodes(Enum):
    success = 'JD_CRUD_S200'
    missing_ent_attrs_error = "JD_CRUD_E400"
    empty_ent_attrs_error = "JD_CRUD_E401"
    save_ent_error = "JD_CRUD_E403"
    del_ent_error = "JD_CRUD_E404"
    get_ent_error = "JD_CRUD_E405"
    server_error = "JD_CRUD_E500"


def insert_into_wr_clients():
    db_con = dbUtils.getConnFromPool()
    cursor = db_con.cursor()
    try:
        _logger.debug('inside insert_into_wr_clients')
        params = None

        sql = """ select id from tenants"""
        _logger.debug(cursor.mogrify(sql, params))
        cursor.execute(sql, params)

        tenants = cursor.fetchall()

        for tenant in tenants:
            tid = tenant[0]
            sql = """ insert into wr_clients(client_name, tenant_id)
                        select distinct(wr_jds.client), tid from wr_jds join tenant_user_roles
                        on wr_jds.recruiter_id = tenant_user_roles.uid
                        where wr_jds.recruiter_id in (select uid from tenant_user_roles where tid=%s)"""
            params = (tid,)
            _logger.debug(cursor.mogrify(sql, params))
            cursor.execute(sql, params)
        db_con.commit()

    except Exception as e:
        _logger.error(e)
        db_con.rollback()
        return (RetCodes.server_error.value, str(e), None)
    finally:
        if cursor is not None:
            cursor.close()
        dbUtils.returnToPool(db_con)

def add_client_id_to_wr_jds():
    db_con = dbUtils.getConnFromPool()
    cursor = db_con.cursor()
    try:
        _logger.debug('inside insert_into_wr_clients')
        db_con = dbUtils.getConnFromPool()
        cursor = db_con.cursor()

        sql = """ select id from tenants"""
        params = None
        _logger.debug(cursor.mogrify(sql, params))
        cursor.execute(sql, params)
        tenants = cursor.fetchall()

        for tenant in tenants:
            tid = tenant[0]
            sql = "select id,client from wr_jds where wr_jds.recruiter_id in (select uid from tenant_user_roles where tid=%s) "
            params = (tid,)
            _logger.debug(cursor.mogrify(sql, params))
            cursor.execute(sql, params)
            jobs = cursor.fetchall()

            for job in jobs:
                client = job[1]
                sql ="""
                update wr_jds set 
                client_id = ( select client_id from wr_clients where client_name = %s and tenant_id = %s)
                where wr_jds.id = %s
                """
                params = (client,tid,job[0])
                _logger.debug(cursor.mogrify(sql, params))
                cursor.execute(sql, params)

        db_con.commit()

    except Exception as e:
        _logger.error(e)
        db_con.rollback()
        return (RetCodes.server_error.value, str(e), None)
    finally:
        if cursor is not None:
            cursor.close()
        dbUtils.returnToPool(db_con)

insert_into_wr_clients()
add_client_id_to_wr_jds()