import psycopg2
import psycopg2.extras
import os

from psycopg2 import pool
__DBPOOL__ = None

def getConnFromPool():
    try:
        global __DBPOOL__
        if __DBPOOL__ == None:
            print(os.environ.get("DB_NAME"))
            __DBPOOL__ = psycopg2.pool.ThreadedConnectionPool(5, 20,user = os.environ.get("DB_USER"),
                                              password = os.environ.get("DB_PASSWORD"),
                                              host = os.environ.get("DB_HOST"),
                                              port = os.environ.get("DB_PORT"),
                                              database = os.environ.get("DB_NAME"))
            print("Connection pool created successfully using ThreadedConnectionPool")


        # Use getconn() method to Get Connection from connection pool
        return __DBPOOL__.getconn()

    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while connecting to PostgreSQL", error)
        return None

def returnToPool(conn):
    global __DBPOOL__

    if __DBPOOL__ != None:
        __DBPOOL__.putconn(conn, key=None, close=False)
        print ( "connection returned to pool successfully.")

def getDictCursor(conn):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    return cursor

def getNamedTupleCursor(conn):
    cursor = conn.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)
    return cursor