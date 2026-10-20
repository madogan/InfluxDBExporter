import datetime
import oracledb
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
        username: str,
        password: str,
        sid: str = None,
        service_name: str = None,
    ):
        self.host = host
        self.port = port
        self.sid = sid
        self.service_name = service_name
        self.user = username
        self.password = password

        if bool(sid) == bool(service_name):
            raise ValueError("Specify exactly one of sid or service_name")


    def connect(self) -> bool:
        if self.service_name:
            dsn = oracledb.makedsn(
                host=self.host,
                port=self.port,
                service_name=self.service_name,
            )
        else:
            dsn = oracledb.makedsn(
                host=self.host,
                port=self.port,
                sid=self.sid,
            )

        self.connection = oracledb.connect(
            user=self.user,
            password=decrypt(self.password),
            dsn=dsn,
        )
        self.cursor = self.connection.cursor()
        return True

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
