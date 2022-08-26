# Change Log

## [2.2.0] - 2022-07-22

- Chore - update linux amd64 oracle client to 21.6

## [2.1.3] - 2022-06-09

- Fix - set exec permissions

## [2.1.2] - 2022-05-17

- Fix libs for rhel/centos 7.x

## [2.1.1] - 2022-05-17

- Add libs for rhel/centos 7.x

## [2.1.0] - 2022-05-05

- Reduce size of Linux zip

## [2.0.9] - 2022-03-03

- Re-implement timezone translation

## [2.0.8] - 2022-01-13

- Adds error message that warns user when response message size is larger than 16Mb
- Adds the option to compile back-end for ARM64 processors

## [2.0.7] - 2022-01-10

- Chore: Update Licensing

## [2.0.6] - 2021-08-10

- Adds documentation for RHEL 8 libnsl dependency
- Fixes an issue where hidden queries were still being executed
- Fixes an issue where queries with just whitespace (empty) were being executed.

## [2.0.4] - 2021-4-12

- Chore: Update SDK

## [2.0.2] - 2020-10-09

- Fixed signed plugin issue

## [2.0.1] - 2020-10-06

- Fixed configuration editor to allow tnsname and kerberos options to be selected during manual setup
- Adjusted configuration editor entry field sizes

## [2.0.2] - 2020-10-09

- Fixed signed plugin issue

## [2.0.1] - 2020-10-06

- Fixed configuration editor to allow tnsname and kerberos options to be selected during manual setup
- Adjusted configuration editor entry field sizes

## [2.0.0] - 2020-10-01

- Compatible with Grafana v7.1+

Key Features:

- Conversion to dataframes for easier use with different visualizations and data transformations
- Updated to use InstantClient v19, supporting stcp connections
- Query editor now uses monaco for syntax

Bugfixes:

- Connection cache will expire idle connections to prevent slow responses

Note: Time Zone support not included in v2.0.0, to be added in next minor release.
All connections and results are processed as UTC.

## [1.2.2] - 2020-08-28

- Fix for kerberos authentication error output

## [1.2.1] - 2020-08-19

- NEW: Support for TNSNAMES and Kerberos Authentication
- Fix for issue #133 (redact message on connection error)
- Fix field comparisons for Annotation Queries
- Increase max message size to 16MB

## [1.2.0] - 2020-05-15

- Now compatible with Grafana v7.0.0
- Now grafana-cli installable

## [1.1.7] - 2020-02-21

- Fix for Edge Browser

## [1.1.6] - 2020-02-21

- New fill options for macros (intervals now the same as other sql datasources)
- New timezone configuration setting for datasource (default is UTC)
- FIX: removed auto-quoting of time columns in macros

## [1.1.5] - 2020-02-05

- Better handling of macro $__timeGroup
- Implements fill options for $__timeGroup similar to other sql datasources
- Upgrade build to go-1.13.7
- Converted to go mod
- Additional test coverage

## [1.1.4] - 2020-

- Connection pool size is now working
- Profiling setting now working
- Fix for backend crash when nil values are return
- Fix for locking issue causing backend to hang
- Fix quoting issues
- Implement braces for macros
- Now allows sql statements inside macros

## [1.1.3] - 2019-12-18

- GF_PLUGIN_ORACLE_DATASOURCE_POOLSIZE can be used to increase/decrease the size of the connection pool with Oracle. The new default is `50`

## [1.1.2] - 2019-11-04

- GF_PLUGIN_PROFILER must be set to "oracle-datasource" to enable profiling. default is false.

## [1.1.1] - 2019-09-20

- Remove connection string output from debug mode
- Refactor to clean up golint warnings

## [1.1.0] - 2019-07-20

- Fixes panic of backend plugin on windows
- Update to all package dependencies

## [1.0.9] - 2019-06-10

- Return message when query results are too large
- Prevent crash due to attempting too large response
- Additional handling of nullable columns
- Updated packages

## [1.0.8] - 2019-05-15

- Now handles nullable column for value field when transforming to timeseries

## [1.0.7] - 2019-05-09

- lower query cache TTL to 60 seconds
- fix leak due to deferred close inside loop
- reuse fingerprint vs recalculating (small performance gain)
- detect errors iterating rows
- add more debug output
- updated vendored packages

## [1.0.6] - 2019-04-25

- Now provides info level log line when type is not matched
- Added additional datatypes
  - converts to type FLOAT: SQLT_INT, SQLT_UIN, SQLT_FLT, SQLT_VNU, SQLT_LNG, SQLT_BFLOAT, SQLT_BDOUBLE
  - converts to type STRING: SQLT_STR, SQLT_LVC, SQLT_VST, SQLT_VBI, SQLT_LBI, SQLT_LVB
  - converts to type DATE: SQLT_DATE
  - converts to type BYTES: SQLT_FILE
- Bugfix: when a query returns no results (and datatypes as a part of the results), the types are not cached to allow future queries with results update the cache

## [1.0.5] - 2019-04-08

- gRPC: hardcode message size to 16MB vs 4MB
- enable alerting

## [1.0.4] - 2019-03-29

- Plugin now links oracle libraries from plugin directory, no need for installation externally on system (linux only, windows requires install)

## [1.0.3] - 2019-03-18

- Support additional field type SQLT_NUME
- Better type conversions
- Add quoted time field to variable interpolation

## [1.0.2] - 2019-03-04

- Update golang dependencies

## [1.0.1] - 2019-02-05

### Fixed

[#13](https://github.com/grafana/oracle-datasource/issues/13)

- High CPU utilization issue fix via short-term cache of column types
- Connection errors fixed by testing cached connections before returning to caller

## [0.0.1] - 2018-05-09

Initial Release