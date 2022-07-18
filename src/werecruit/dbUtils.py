import psycopg2
import psycopg2.extras
import os
import logging
_logger = logging.getLogger()

from psycopg2 import pool
__DBPOOL__ = None

def getConnFromPool():
    try:
        global __DBPOOL__
        if __DBPOOL__ == None:
            _logger.debug(os.environ.get("DB_NAME"))
            #print(os.environ.get("DB_PASSWORD"))
            _logger.debug(os.environ.get("DB_HOST"))
            _logger.debug(os.environ.get("DB_PORT"))
            _logger.debug(os.environ.get("DB_USER"))

            __DBPOOL__ = psycopg2.pool.ThreadedConnectionPool(5, 20,user = os.environ.get("DB_USER"),
                                              password = os.environ.get("DB_PASSWORD"),
                                              host = os.environ.get("DB_HOST"),
                                              port = os.environ.get("DB_PORT"),
                                              database = os.environ.get("DB_NAME"))
            _logger.debug("Connection pool created successfully using ThreadedConnectionPool")


        # Use getconn() method to Get Connection from connection pool
        return __DBPOOL__.getconn()

    except (Exception, psycopg2.DatabaseError) as error :
        _logger.error ("Error while connecting to PostgreSQL", exc_info=1)
        return None

def returnToPool(conn):
    global __DBPOOL__

    if __DBPOOL__ != None:
        __DBPOOL__.putconn(conn, key=None, close=False)
        _logger.debug ( "connection returned to pool successfully.")

def getDictCursor(conn):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    return cursor

def getNamedTupleCursor(conn):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)
    return cursor