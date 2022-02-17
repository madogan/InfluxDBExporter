import random
import datetime
import time

from connectors.mssql_connector import MSSqlConnector
from connectors.oracle_connector import OracleConnector


# Connect to oracle with OracleConnector.
oracle_connector = OracleConnector(
    host='localhost',
    port=1521,
    sid='xe',
    username='system',
    password='oracle',
)
oracle_connector.connect()

# Connect to mssql with MSSqlConnector.
mssql_connector = MSSqlConnector(
    host='localhost',
    port= 1433,
    username= 'sa',
    password='qweQWE123*',
)
mssql_connector.connect()

try:
    oracle_connector.execute('''
    CREATE TABLE test (
        f float, i number, ts timestamp
    )
    ''')
except Exception as e:
    print(e)

try:
    mssql_connector.execute('''
    CREATE TABLE test (
        f float, i int, ts datetime
    )
    ''')
except Exception as e:
    print(e)

amount = 3 * 24 * 60 * 60
ts_start = datetime.datetime.now()
for i in range(1, amount):
    time.sleep(1)
    oracle_connector.execute(
        'insert into test(f, i, ts) values(:f, :i, :ts)',
        [
            random.random(),
            random.randint(0, 1500),
            datetime.datetime.now()
        ],
    )
    mssql_connector.execute(
        'INSERT INTO test (f, i, ts) VALUES (%s, %s, %s);',
        (
            random.random(),
            random.randint(0, 1500),
            datetime.datetime.now()
        ),
    )
    print(f'Inserted: {i} | Total: {amount} | Left: {amount - i}', end='\r')

mssql_connector.close()
oracle_connector.close()
