import os
import re
import sys
import time
import pytz
import datetime

from loguru import logger
from parsers import parse_config
from connectors.mssql_connector import MSSqlConnector
from connectors.influx_connector import InfluxConnector
from connectors.oracle_connector import OracleConnector
from apscheduler.schedulers.background import BackgroundScheduler
from models import Job, OracleConnection, MSSqlConnection, InfluxConnection
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

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


def execute_job(influx: InfluxConnection, job: Job):
    try:
        now = datetime.datetime.now()

        if now.hour >= 23 and now.minute >= 58:
            return

        if now.hour <= 0 and now.minute <= 2:
            return

        if type(job.connection) == OracleConnection:
            connection_connector = OracleConnector(**job.connection.json())
        elif type(job.connection) == MSSqlConnection:
            connection_connector = MSSqlConnector(**job.connection.json())
        else:
            raise Exception(f'Unknown database type: {type(job.connection)}')

        logger.info('\n' + '#' * 50)
        logger.info(f'Running job: {job.name}')
        logger.info(f'Query: {job.query}')
        logger.info(f'Tags: {job.tags}')
        logger.info(f'Interval: {job.interval}')

        destination = InfluxConnector(**influx.json())
        destination.connect()
        connection_connector.connect()

        points = []
        rows = connection_connector.fetchall(re.sub('\s+', ' ', job.query, re.I | re.M))
        logger.info(f'{len(rows)} are fetched from {job.connection.name}')
        for row in rows:
            ts = row.pop(job.time_column_name, None)

            if not ts:
                logger.error('Time column is not found, stamping now!')
                ts = datetime.datetime.now()

            if type(ts) == str:
                ts = datetime.datetime.strptime(ts, job.time_column_format)

            ts = ts.replace(
                year=now.year,
                month=now.month,
                day=now.day,
            ).astimezone(tz=pytz.utc)

            keys = list(row.keys())
            for key in keys:
                if row[key] == None:
                    row.pop(key)

            if len(row) == 0:
                continue

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
