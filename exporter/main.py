import os
import re
import sys
import time
from typing import Union
import pytz
import datetime

from loguru import logger
from parsers import parse_config
from connectors.api_connector import APIConnector
from connectors.mssql_connector import MSSqlConnector
from connectors.influx_connector import InfluxConnector
from connectors.oracle_connector import OracleConnector
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from models import APIJob,DatabaseJob, OracleConnection, MSSqlConnection, InfluxConnection, APIConnection


logger.remove(0)
logger.add(
    sys.stdout,
    format="[{time}] [{level}] {message}",
    level="INFO",
    colorize=True
)
logger.add(
    "./logs/influxdbexport.log",
    format="[{time}] [{level}] {message}",
    rotation="100 MB",
    retention="7 days"
)


def execute_job(influx: InfluxConnection, job: Union[DatabaseJob, APIJob]):
    try:
        now = datetime.datetime.now()

        if now.hour >= 23 and now.minute >= 58:
            return

        if now.hour <= 0 and now.minute <= 2:
            return

        logger.info('\n' + '#' * 50)
        logger.info(f'Running job: {job.name}')
        logger.info(f'Tags: {job.tags}')
        logger.info(f'Interval: {job.interval}')

        destination = InfluxConnector(**influx.json())
        destination.connect()

        if isinstance(job.connection, OracleConnection):
            connection_connector = OracleConnector(**job.connection.dict())
        elif isinstance(job.connection, MSSqlConnection):
            connection_connector = MSSqlConnector(**job.connection.dict())
        elif isinstance(job.connection, APIConnection):
            connection_connector = APIConnector(**job.connection.dict())
        else:
            raise Exception(f'Unknown database type: {type(job.connection)}')

        connection_connector.connect()

        points = []
        if isinstance(connection_connector, APIConnector):
            rows = connection_connector.fetchall(job.endpoint, job.key, job.label)
        else:
            rows = connection_connector.fetchall(job.query)

        for row in rows:
            ts = row.pop(job.time_column_name, None) or datetime.datetime.utcnow()

            if isinstance(ts, str):
                ts = datetime.datetime.strptime(ts, job.time_column_format)

            ts = ts.replace(year=now.year, month=now.month, day=now.day).astimezone(tz=pytz.utc)

            row = {k: v for k, v in row.items() if v is not None}
            
            if row:
                point = {
                    'measurement': job.name,
                    'tags': job.tags,
                    'time': ts,
                    'fields': row
                }
                points.append(point)

        result = False
        
        if len(points) > 0:
            logger.info(f'First Point: {" ".join(f"{k}={v}" for k, v in points[0].items())}')
            logger.info(f'Last Point: {" ".join(f"{k}={v}" for k, v in points[-1].items())}')

            result = destination.write_points(points)

        logger.info(f'({result}) {job.name} {len(points)} points are inserted!')

        connection_connector.close()
        destination.close()
    except Exception as e:
        logger.exception(e)


def main():
    logger.info('Starting...')
    config_path = sys.argv[1].strip()
    logger.info(f'Config path: {config_path}')
    config = parse_config(config_path)
    logger.info(f'Config: {config}')

    scheduler = BackgroundScheduler(
        executors = {
            'default': ThreadPoolExecutor(100),
            'processpool': ProcessPoolExecutor(10)
        },
        job_defaults={
            'coalescing': False,
            'max_instances': 3,
        }
    )
    
    logger.info('Scheduling...')
    for job in config.jobs.values():
        logger.info(f'Scheduling job "{job.name}" with interval "{job.interval}"')

        seconds = job.interval.total_seconds()
        scheduler.add_job(
            execute_job, 
            'interval', 
            seconds=job.interval.total_seconds(),
            misfire_grace_time=int(seconds-3),
            args=(config.influx, job)
        )

    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()


if __name__ == '__main__':
    main()
