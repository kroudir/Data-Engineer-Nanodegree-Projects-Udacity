import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur, conn):
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    print('1. Connected')
    cur = conn.cursor()
    print('2. Created Cursor')

    drop_tables(cur, conn)
    print('3. Dropped tables if already exists')
    create_tables(cur, conn)
    print('4.Created tables')

    conn.close()
    print('5. Closed the connection')

if __name__ == "__main__":
    main()