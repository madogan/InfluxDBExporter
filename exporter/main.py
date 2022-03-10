import re
import sys
import time
import datetime
import pytz
import schedule

from loguru import logger
from parsers import parse_config
from models import Job, OracleConnection, MSSqlConnection, InfluxConnection
from connectors.mssql_connector import MSSqlConnector
from connectors.influx_connector import InfluxConnector
from connectors.oracle_connector import OracleConnector

logger.remove(0)
logger.add(
    sys.stdout,
    format="[{time}] [{level}] {message}",
    level="INFO",
    colorize=True
)
logger.add(
    "/var/log/influxdbexporter/influxdbexport.log",
    format="[{time}] [{level}] {message}",
    rotation="250 MB"
)


def execute_job(influx: InfluxConnection, job: Job):
    try:
        now = datetime.datetime.now()

        if now.hour >= 23 and now.minute >= 55:
            return

        if now.hour <= 0 and now.minute <= 5:
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

            if not time:
                logger.error('Time column is not found')
                continue

            if type(ts) == str:
                ts = datetime.datetime.strptime(ts, '%H:%M')

            ts = ts.replace(
                year=now.year,
                month=now.month,
                day=now.day,
            ).astimezone(tz=pytz.utc)

            point = {
                'measurement': job.name,
                'tags': job.tags,
                'time': ts,
                'fields': row
            }
            points.append(point)

        result = False
        
        if len(points) > 0:
            logger.info(
                f'First Point: {" ".join(f"{k}={v}" for k, v in points[0].items())}')
            logger.info(
                f'Last Point: {" ".join(f"{k}={v}" for k, v in points[-1].items())}')

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

    logger.info('Scheduling...')
    for job in config.jobs.values():
        logger.info(
            f'Scheduling job "{job.name}" with interval "{job.interval}"')
        schedule.every(
            job.interval.total_seconds()
        ).seconds.do(
            execute_job, config.influx, job
        )

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
