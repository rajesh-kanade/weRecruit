import psycopg2
from psycopg2 import pool
__DBPOOL__ = None

def getConnFromPool():
    try:
        global __DBPOOL__
        if __DBPOOL__ == None:
            __DBPOOL__ = psycopg2.pool.ThreadedConnectionPool(5, 20,user = "postgres",
                                              password = "rajaram1909",
                                              host = "127.0.0.1",
                                              port = "5432",
                                              database = "wemoodle1")
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
