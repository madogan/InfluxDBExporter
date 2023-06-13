import re
import datetime

from enum import Enum
from typing import Dict, List, Union
from pydantic import BaseModel, validator


class DatabaseType(Enum):
    oracle = "oracle"
    mssql = "mssql"
    influx = "influx"
    api = "api"


class MSSqlConnection(BaseModel):
    name: str
    host: str
    port: int
    username: str
    password: str
    database: str = None
    instancename: str = None

    def json(self):
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "database": self.database,
            "instancename": self.instancename,
        }


class InfluxConnection(BaseModel):
    host: str
    port: int
    username: str
    password: str
    database: str

    def json(self):
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "database": self.database,
        }


class OracleConnection(BaseModel):
    name: str
    host: str
    port: int
    sid: str
    username: str
    password: str

    def json(self):
        return {
            "host": self.host,
            "port": self.port,
            "sid": self.sid,
            "username": self.username,
            "password": self.password,
        }


class APIConnection(BaseModel):
    name: str
    url: str
    
    def json(self):
        return {
            "url": self.url,
        }


class BaseJob(BaseModel):
    name: str
    interval: datetime.timedelta
    tags: Dict = {}

    @validator('tags', pre=True)
    def validate_tags(cls, v):
        for key, val in v.items():
            for i in val:
                v[key] = i.strip()
        return v

    @validator('interval', pre=True)
    def validate_interval(cls, v):
        interval_json = {
            'days': 0,
            'hours': 0,
            'minutes': 0,
            'seconds': 0,
        }
        v = v.strip()
        match = re.match(r'(\d*d)?(\d*h)?(\d*m)?(\d*[ms])', v, re.I)

        for g in match.groups():
            if g is None:
                continue

            gint = int(g[:-1])
            if g.endswith('d'):
                interval_json['days'] = gint
            elif g.endswith('h'):
                interval_json['hours'] = gint
            elif g.endswith('m'):
                interval_json['minutes'] = gint
            elif g.endswith('s'):
                interval_json['seconds'] = gint
            else:
                raise ValueError('Wrong format!')

        return datetime.timedelta(**interval_json)


class APIJob(BaseJob):
    connection: APIConnection
    endpoint: str
    key: str
    label: str = None
    
    @validator('endpoint', pre=True)
    def clean_endpoint_string(cls, v):
        return re.sub(r'\s+', ' ', v).strip()

    @validator('label', pre=True)
    def assign_key_if_none(cls, label, values):
        if label is None:
            return values['key']
        return label


class DatabaseJob(BaseJob):
    connection: Union[OracleConnection, MSSqlConnection]
    time_column_name: str = None
    time_column_format: str = '%H:%M'
    query: str
    columns: List[str] = []

    @validator('query', pre=True)
    def clean_query_string(cls, v):
        return re.sub(r'\s+', ' ', v).strip()


class Config(BaseModel):
    influx: InfluxConnection = None
    jobs: Dict[str, Union[APIJob, DatabaseJob]] = {}
