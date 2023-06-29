"""
CREATE TABLE "adl_activity_data" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "activity" TEXT NOT NULL,
    "time" TIMESTAMP(3) NOT NULL UNIQUE DEFAULT CURRENT_TIMESTAMP,
    "image_source" TEXT  NULL,
    "sound_source" TEXT  NULL,
    "motion_source" TEXT  NULL,
    "comment" TEXT NULL
);

CREATE INDEX "activity_key" ON "adl_activity_data"("activity");

INSERT INTO public."adl_activity_data" (activity, image_source) values ('read', '/home/adl/test/');

INSERT INTO public."adl_activity_data" (activity, time, image_source) values ('read', '2022-09-08 15:30:20.159', '/home/adl/test/');
"""

import psycopg2
import psycopg2
from psycopg2 import Error

DB_HOST = '10.227.99.196'
DB_HOST = '192.168.1.134'

DB_PORT = '5432'
DB = 'YOUR_CUSTOM_USER'
USER = 'YOUR_CUSTOM_USER'
PWD = 'YOUR_CUSTOM_PASSWORD'

def get_conn():
    conn  = psycopg2.connect(user=USER,
                          password=PWD,
                          host=DB_HOST,
                          port=DB_PORT,
                          database=DB)
    conn.autocommit = True
    return conn


# def insert_adl_activity_data(activity, time, image_source='', sound_source='', motion_source=''):
#     try:
#         sql = 'INSERT INTO public."adl_activity_data" (activity, time, image_source, sound_source, motion_source) values (%s, %s, %s, %s, %s)'
#         # sql = 'INSERT INTO public."adl_activity_data" (activity, image_source) values (\'read\', \'/home/adl/test/\')'
#         conn = get_conn()
#         cur = conn.cursor()
#         cur.execute(sql, (activity, time, image_source, sound_source, motion_source))
#         cur.close()
#         # print("Insert success")
#     except (Exception, Error) as error:
#         print("Error while connecting to PostgreSQL", error)
#     finally:
#         if (conn):
#             cur.close()
#             conn.close()
#             print("PostgreSQL connection is closed")

def insert_adl_activity_data(activity, time, image_source='', sound_source='', motion_source='', object_source = ''):
    try:
        sql = 'INSERT INTO public."adl_activity_data" (activity, time, image_source, sound_source, motion_source, object_source) values (%s, %s, %s, %s, %s, %s)'
        # sql = 'INSERT INTO public."adl_activity_data" (activity, image_source) values (\'read\', \'/home/adl/test/\')'
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (activity, time, image_source, sound_source, motion_source, object_source))
        cur.close()
        # print("Insert success")
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (conn):
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")
    

def update_stock(stock_id, symbol, company):
    sql = 'UPDATE stocks SET company=%s, symbol=%s WHERE id=%s'
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (company, symbol, stock_id))
    cur.close()
    conn.close()

def delete(stock_id):
    sql = 'DELETE FROM stocks  WHERE id=%s'
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (stock_id,))
    cur.close()
    conn.close()

def find_all():
    sql = 'SELECT * FROM public."adl_activity_data"'
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    # conn.close()
    return result



def test():
    try:
        # Connect to an existing database
        connection = psycopg2.connect(user=USER,
                                    password=PWD,
                                    host=DB_HOST,
                                    port=DB_PORT,
                                    database=DB)

        # Create a cursor to perform database operations
        cursor = connection.cursor()
        # Print PostgreSQL details
        print("PostgreSQL server information")
        print(connection.get_dsn_parameters(), "\n")
        # Executing a SQL query
        cursor.execute("SELECT version();")
        # Fetch result
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

        print('inster into adl_activity data')
        activity = 'Watch_TV'
        time = '2022-10-01 11:40:31.000'
        image_source = 'livingroom'
        sound_source = 'tv_news'
        motion_source = 'sitting'
        object_source = '_tv'

        insert_adl_activity_data(activity, time, image_source, sound_source, motion_source, object_source)

        res = find_all()
        print('Res find all:', res)


    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


if __name__ == "__main__":
    test()
