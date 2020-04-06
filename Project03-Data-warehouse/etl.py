import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    print('1. Connected')
    cur = conn.cursor()
    print('2. Created Cursor')
    
    load_staging_tables(cur, conn)
    print('2. Loaded to staging')
    insert_tables(cur, conn)
    print('3. Inserted into tables')

    conn.close()
    print('4. Closed the connection')


if __name__ == "__main__":
    main()