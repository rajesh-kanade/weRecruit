import dbUtils
from enum import Enum
import logging
_logger = logging.getLogger()


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
        db_con = dbUtils.getConnFromPool()
        cursor = db_con.cursor()
        params = None

        sql = """ select * from tenants"""
        _logger.debug(cursor.mogrify(sql, params))
        cursor.execute(sql, params)

        tenants = cursor.fetchall()

        for tenant in tenants:
            tid = tenant[3]
            sql = """ select * from tenant_user_roles where tid=%s"""
            params = (tid,)
            _logger.debug(cursor.mogrify(sql, params))
            cursor.execute(sql, params)

            users = cursor.fetchall()

            for user in users:
                uid = user[1]
                sql = """ insert into wr_clients(client_name, tenant_id)
                        select distinct(wr_jds.client), tid from wr_jds, tenant_user_roles
                        where wr_jds.recruiter_id = %s"""
                params = (uid,)
                _logger.debug(cursor.mogrify(sql, params))
                cursor.execute(sql, params)

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

        sql = """ select * from tenants"""
        params = None
        _logger.debug(cursor.mogrify(sql, params))
        cursor.execute(sql, params)
        cursor.execute(sql)

        tenants = cursor.fetchall()

        for tenant in tenants:
            tid = tenant[3]
            sql = """ update wr_jds
                    set client_id = (select client_id from wr_clients where wr_jds.client=wr_clients.client_name
                    and wr_jds.recruiter_id in (select uid from tenant_user_roles where tid=%s))
                """
            params = (tid,)
            _logger.debug(cursor.mogrify(sql, params))
            cursor.execute(sql, params)

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