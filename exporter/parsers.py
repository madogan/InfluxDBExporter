import yaml

from models import Config, InfluxConnection, MSSqlConnection, OracleConnection, APIConnection, APIJob, DatabaseJob


def parse_config(path: str) -> Config:
    with open(path, 'rt') as fp:
        data = yaml.safe_load(fp.read())

    config = Config(influx=InfluxConnection(**data['influx']))

    connections = {
        name: {
            'oracle': OracleConnection,
            'mssql': MSSqlConnection,
            'api': APIConnection
        }[values.pop('database_type', None)](name=name, **values)
        for name, values in data['connections'].items()
    }

    job_types = {
        APIConnection: APIJob,
        OracleConnection: DatabaseJob,
        MSSqlConnection: DatabaseJob,
    }

    config.jobs = {
        name: job_types[type(connections[values['connection_name']])](
            name=name,
            connection=connections[values['connection_name']],
            **values
        )
        for name, values in data['jobs'].items()
    }

    return config