import datetime
import os
import re
import cx_Oracle
import pytz

from aes import decrypt
from typing import Any, List


class OracleConnector:
    connection = None
    cursor = None

    def __init__(
        self,
        host: str,
        port: int,
        sid: str,
        username: str,
        password: str
    ):
        self.host = host
        self.port = port
        self.sid = sid
        self.user = username
        self.password = password

        lib_dir = os.environ.get('LD_LIBRARY_PATH', None)

        if not lib_dir:
            raise ValueError('LD_LIBRARY_PATH is not set!')

        try:
            cx_Oracle.init_oracle_client(lib_dir=lib_dir)
        except Exception as e:
            print('Oracle client already initiliazed.')

    def connect(self) -> bool:
        self.connection = cx_Oracle.connect(
            user=self.user, password=decrypt(self.password), dsn=cx_Oracle.makedsn(
                host=self.host,
                port=self.port,
                sid=self.sid,
            ) ,
        )
        self.cursor = self.connection.cursor()
    
    def execute(self, sql: str, data: List = []) -> Any:
        self.cursor.execute(
            sql,
            data,
        )
        self.connection.commit()

    def fetchall(self, sql: str, data: List = []) -> Any:
        self.cursor.execute(sql, data)
        columns = [col[0] for col in self.cursor.description]
        self.cursor.rowfactory = lambda *args: dict(zip(columns, args))
        return self.cursor.fetchall()

    def close(self) -> bool:
        self.cursor.close()
        self.connection.close()
