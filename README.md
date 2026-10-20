# InfluxDB Exporter

InfluxDB Exporter collects data from relational databases and writes it to InfluxDB as time-series data. The exported metrics can then be queried and visualized using Grafana.

## Architecture

```text
Oracle Database
      |
      v
InfluxDB Exporter
      |
      v
InfluxDB
      |
      v
Grafana Dashboards
```

The exporter periodically executes SQL queries against configured database connections, retrieves the selected columns, and writes the results to InfluxDB. Grafana can then use InfluxDB as a data source to build dashboards and visualize historical data.

## Features

- Oracle Database connectivity using `python-oracledb`
- Oracle connections using either a SID or a service name
- Configurable SQL queries and polling intervals
- Selection of columns to export
- Time-column support for time-series data
- InfluxDB as the time-series storage backend
- Grafana integration for visualization
- Support for additional database connectors configured by the project

## Requirements

- Python
- InfluxDB
- Oracle Database, when using the Oracle connector
- Oracle Database connectivity supported by `python-oracledb`
- Grafana, for dashboards and visualization

Install the Python dependencies:

```bash
pip install -r exporter/requirements.txt
```

## Configuration

Configure the InfluxDB destination, database connections, and export jobs in `config.yaml`.

Example Oracle connection using a service name:

```yaml
connections:
  oracle:
    database_type: oracle
    host: localhost
    port: 1521
    service_name: ORCLPDB1
    username: system
    password: "<encrypted-password>"
```

For databases configured with a SID, use `sid` instead of `service_name`.

Specify exactly one of `sid` or `service_name` for an Oracle connection.

Example export job:

```yaml
jobs:
  oracle_test:
    interval: 5s
    connection_name: oracle
    columns:
      - F
      - I
      - TS
    time_column_name: TS
    query: SELECT f, i, ts FROM test
```

Adapt the query, selected columns, connection name, and time column to your database schema.

## Grafana Integration

1. Start InfluxDB and configure it as a data source in Grafana.
2. Run the exporter with your `config.yaml` configuration.
3. Create a Grafana dashboard and select the exported time-series data.
4. Use panels to visualize values over time, compare metrics, and monitor database activity.

The exact query syntax in Grafana depends on your InfluxDB version and configured query language.

## Security

- Do not commit production passwords, access tokens, or other sensitive credentials.
- Protect the configuration file and restrict access to it.
- Use encrypted credentials only as supported by the project's encryption implementation.
- Apply least-privilege database permissions to exporter accounts.

## Contributing

Contributions, bug reports, and improvements are welcome. Please include relevant configuration details and test results when submitting changes.

## License

See the repository's license file for the applicable license terms.
