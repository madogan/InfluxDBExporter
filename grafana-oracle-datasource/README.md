# Oracle data source for Grafana

## Requirements

This plugin has the following requirements:
* An Oracle instance with at least one user
* One of the following account types:
    * Grafana Cloud: Pro customers, Advanced customers, or Pro trial users with the Enterprise plugin add-on enabled
    * Grafana Enterprise: Customers with an [activated license](https://grafana.com/docs/grafana/latest/enterprise/license/activate-license/) and a user with Grafana server or organization administration [permissions](https://grafana.com/docs/grafana/latest/permissions/)
* The Enterprise plugin add-on enabled

## Known limitations

In the Oracle data source settings the default timezone cannot be changed. Instead you can apply an offset to times in the query editor.

## Install the data source

To install the data source, refer to [Installation](https://grafana.com/grafana/plugins/grafana-oracle-datasource/?tab=installation).

### Configure the data source

Set up an Oracle database user with only SELECT permissions on the databases and tables you want to query. Grafana does *not* validate that queries are safe. Queries can contain any SQL statement. For example, statements like `DELETE FROM user;` and `DROP TABLE user;` would be executed.

Follow [these instructions](https://grafana.com/docs/grafana/latest/datasources/add-a-data-source/) to add a new Oracle data source, and choose from three datasource configuration options:

* **Host with TCP Port with basic authentication**

  | Field                          | Option                                   |
  | ------------------------------ | ---------------------------------------- |
  | Enable TNSNames                | disable                                  |
  | Host                           | hostname (or IP address) and port number |
  | Database                       | database name                            |
  | Enable Kerberos Authentication | disable                                  |
  | User                           | Oracle username                          |
  | Password                       | Oracle user's password                   |

* **TNSNames entry with basic authentication**

  | Field                          | Option                                     |
  | ------------------------------ | ------------------------------------------ |
  | Enable TNSNames                | enable                                     |
  | TNSNAME                        | Any valid entry found in your tnsnames.ora |
  | Enable Kerberos Authentication | disable                                    |
  | User                           | Oracle username                            |
  | Password                       | Oracle user's password                     |


* **TNSNames entry with Kerberos authentication**
  
  To learn more about kerberos, refer to [kerberos](kerberos)
 
  | Field                          | Option                                     |
  | ------------------------------ | ------------------------------------------ |
  | Enable TNSNames                | enable                                     |
  | TNSNAME                        | Any valid entry found in your tnsnames.ora |
  | Enable Kerberos Authentication | enable                                     |


### Configure the data source with provisioning

Data sources can be configured with Grafana’s provisioning system. You can read more about how it works and all the settings you can set for data sources on [the provisioning docs page](https://grafana.com/docs/grafana/latest/administration/provisioning/#datasources)

Here is a provisioning examples for this data source

TNSNames enabled with basic auth:
```yaml
apiVersion: 1

datasources:
  - name: Oracle (TNS-BASICAUTH)
    type: grafana-oracle-datasource
    access: proxy
    basicAuth: false
    editable: true
    jsonData:
      timezone_name: UTC
      useKerberosAuthentication: false
      useTNSNamesBasedConnection: true
      user: USERNAME
    secureJsonData:
      password: PASSWORD
    url: TNSNAME
    version: 1
```
TNSNames disabled with basic auth:
```yaml
apiVersion: 1

datasources:
  - name: Oracle (Integration)
    type: grafana-oracle-datasource
    access: proxy
    basicAuth: false
    editable: true
    jsonData:
      database: DATABASE
      user: USERNAME
    secureJsonData:
      password: PASSWORD
    url: HOST
    version: 1
```

## Query the data source

The query editor allows you to query Oracle to return time series data or a table. Queries can contain macros which simplify syntax and allow for dynamic parts.

### Query as time series

If you set `Format as` to `Time series`, for use in Graph panel for example, then the query must return a column named `time` that returns either a sql datetime or any numeric datatype representing unix epoch in seconds.
Grafana interprets DATE and TIMESTAMP columns without explicit time zone as UTC.
Any column except `time` and `metric` is treated as a value column.
You may return a column named `metric` that is used as metric name for the value column.

Example with `metric` column

```sql
SELECT
  $__timeGroup(time_date_time, '5m') AS time,
  MIN(value_double),
  'MIN' as metric
FROM test_data
WHERE $__timeFilter(time_date_time)
GROUP BY $__timeGroup(time_date_time, '5m')
ORDER BY time

```

### Query as table

If the `Format as` query option is set to `Table` then you can basically do any type of SQL query. The table panel will automatically show the results of whatever columns & rows your query returns. You can control the name of the Table panel columns by using regular `as` SQL column selection syntax.

### Macros

To simplify syntax and to allow for dynamic parts, like date range filters, the query can contain macros.

| Macro example                                | Description                                                                                                                                                                                                                                          |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| *$__time(dateColumn)*                        | Will be replaced by an expression to rename the column to `time`. For example, `dateColumn as time`                                                                                                                                                  |
| *$__timeEpoch(dateColumn)*                   | Will be replaced by an expression to rename the column to `time` and converting the value to unix timestamp (in milliseconds).                                                                                                                       |
| *$__timeFilter(dateColumn)*                  | Will be replaced by a time range filter using the specified column name. For example, `dateColumn BETWEEN TO_DATE('19700101','yyyymmdd') + (1/24/60/60/1000) * 1500376552001 AND TO_DATE('19700101','yyyymmdd') + (1/24/60/60/1000) * 1500376552002` |
| *$__timeFrom()*                              | Will be replaced by the start of the currently active time selection converted to `DATE` data type. For example, `TO_DATE('19700101','yyyymmdd') + (1/24/60/60/1000) * 1500376552001`                                                                |
| *$__timeTo()*                                | Will be replaced by the end of the currently active time selection converted to `DATE` data type.                                                                                                                                                    |
| *$__timeGroup(dateColumn,'5m')*              | Will be replaced by an expression usable in GROUP BY clause.                                                                                                                                                                                         |
| *$__timeGroup(dateColumn,‘5m’[, fillvalue])* | Will be replaced by an expression usable in GROUP BY clause. Providing a fillValue of NULL or floating value will automatically fill empty series in timerange with that value. For example, $__timeGroup{createdAt, '1m', 0}.                       |
| *$__timeGroup(dateColumn,‘5m’, 0)*           | Same as above but with a fill parameter so missing points in that series will be added by grafana and 0 will be used as value.                                                                                                                       |
| *$__timeGroup(dateColumn,‘5m’, NULL)*        | Same as above but NULL will be used as value for missing points.                                                                                                                                                                                     |
| *$__timeGroup(dateColumn,‘5m’, previous)*    | Same as above but the previous value in that series will be used as fill value if no value has been seen yet NULL will be used.                                                                                                                      |
| *$__unixEpochFilter(dateColumn)*             | Will be replaced by a time range filter using the specified column name with times represented as unix timestamp (in milliseconds). For example, `dateColumn >= 1500376552001 AND dateColumn <= 1500376552002`                                       |
| *$__unixEpochFrom()*                         | Will be replaced by the start of the currently active time selection as unix timestamp. For example, `1500376552001`                                                                                                                                 |
| *$__unixEpochTo()*                           | Will be replaced by the end of the currently active time selection as unix timestamp. For example, `1500376552002`                                                                                                                                   |

The plugin also supports notation using braces `{}`. Use this notation when queries are needed inside parameters.

NOTE: Use one notation type per query, if the query needs braces, all macros in the query will need to use braces.

```SQL
$__timeGroup{dateColumn,'5m'}
$__timeGroup{SYS_DATE_UTC(SDATE),'5m'}
$__timeGroup{FROM_TZ(CAST(SDATE as timestamp), 'UTC'), '1h'}
```

The query editor has a link named `Generated SQL` that shows up after a query as been executed, while in panel edit mode. Click on it and it will expand and show the raw interpolated SQL string that was executed.

### Templates and variables

Follow [these instructions](https://grafana.com/docs/grafana/latest/variables/variable-types/add-query-variable/) to add a new Oracle query variable. Use your Oracle data source as your data source

Oracle query can return things like measurement names, key names or key values that are shown as a dropdown select box.

Examples:
- you can have a variable that contains all values for the `hostname` column in the `host` table

  ```sql
  SELECT hostname FROM host
  ```

- A query can return multiple columns and Grafana will automatically create a list from them. For example, the query below will return a list with values from `hostname` and `hostname2`.

    ```sql
    SELECT host.hostname, other_host.hostname2 FROM host JOIN other_host ON host.city = other_host.city
  ```

- To use time range dependent macros like `$__timeFilter(column)` in your query the refresh mode of the template variable needs to be set to *On Time Range Change*.

  ```sql
  SELECT event_name FROM event_log WHERE $__timeFilter(time_column)
  ```

- Another option is a query that can create a key/value variable. The query should return two columns that are named `__text` and `__value`. The `__text` column value should be unique (if it is not unique then the first value is used). The options in the dropdown will have a text and value that allows you to have a friendly name as text and an id as the value. An example query with `hostname` as the text and `id` as the value:

  ```sql
  SELECT hostname AS __text, id AS __value FROM host
  ```

- You can also create nested variables. For example if you had another variable named `region`. Then you could have
the hosts variable only show hosts from the current selected region with a query like this (if `region` is a multi-value variable then use the `IN` comparison operator rather than `=` to match against multiple values):

  ```sql
  SELECT hostname FROM host WHERE region IN($region)
  ```

If the variable is a multi-value variable then use the `IN` comparison operator rather than `=` to match against multiple values.

After creating a variable it can be used in your Oracle queries by using [this syntax](https://grafana.com/docs/grafana/latest/variables/syntax/).

For more information on variables refer [this](https://grafana.com/docs/grafana/latest/variables/).

## Get the most out of the plugin

* [Add annotations](https://grafana.com/docs/grafana/latest/dashboards/annotations/)
* [Configure and use template variables](https://grafana.com/docs/grafana/latest/variables/)
* [Add transformations](https://grafana.com/docs/grafana/latest/panels/transformations/)
* [Set up alerting](https://grafana.com/docs/grafana/latest/alerting/)

### Annotation Queries

Annotation queries require results to have columns "time", "text", and "tags" which will be displayed as vertical lines in a graph, which a tooltip that displays the text on mouse-over.

The time value must be in unix epoch "seconds".

A typical timestamp column will need to be cast to unix epoch seconds, see example below.

```SQL
SELECT
  $__time("createdAt"),
  "value"
FROM
  GRAFANA_METRIC
WHERE
  "datacenter" = '$datacenter' AND
  $__timeFilter("createdAt")
```

```SQL
SELECT
  (cast(sys_extract_utc("createdAt") as date) - TO_DATE('1970-01-01 00:00:00','YYYY-MM-DD HH24:MI:SS')) * 86400 as time,
  "message" as text,
  "datacenter" as tags
FROM
  GRAFANA_EVENTS
WHERE  $__timeFilter("createdAt")
```

With template variables included

```SQL
SELECT
  (cast(sys_extract_utc("createdAt") as date) - TO_DATE('1970-01-01 00:00:00','YYYY-MM-DD HH24:MI:SS')) * 86400 as time,
  "message" as text,
  "datacenter" as tags
FROM
  GRAFANA_EVENTS
WHERE  $__timeFilter("createdAt") AND "datacenter" = '$datacenter'
```
