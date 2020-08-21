# Nagios Checks Elasticsearch

Some nagios checks for Elasticsearch. See below for details.

# query_elasticsearch.py

A Nagios plugin that makes ElasticSearch queries.
Tested with Elasticsearch version 7.x

## Requirements

* Elasticsearch python library
* json python library

## Usage:

```sh
query_elasticsearch_acb.py [-h] -H HOSTNAME -U USERNAME -P PASSWORD -i
                                  INDEX -q QUERY [QUERY ...] [-a AGGS]
                                  [-p PERIOD] [-w [WARNING]] [-c [CRITICAL]]
                                  [-d] [-v]

Nagios check for Elasticsearch queries

optional arguments:
  -h, --help            show this help message and exit
  -H HOSTNAME, --hostname HOSTNAME
                        hostname or IP address of Elasticsearch server
  -U USERNAME, --username USERNAME
                        username
  -P PASSWORD, --password PASSWORD
                        user password
  -i INDEX, --index INDEX
                        index where are performed the requests
  -q QUERY [QUERY ...], --query QUERY [QUERY ...]
                        part of the query (i.e : {"match_phrase":{"event.type"
                        :"authentication_failure"}})
  -a AGGS, --aggs AGGS  aggregation terms
  -p PERIOD, --period PERIOD
                        period from now (i.e. 15m)
  -w [WARNING], --warning [WARNING]
                        warning trigger for total records
  -c [CRITICAL], --critical [CRITICAL]
                        critical trigger for total records
  -d, --perfdata        enable Nagios perf data
  -v, --verbose         enable verbose mode
```

## Example

```sh
$ query_elasticsearch.py -H http://127.0.0.1:9200 -U elastic -P password -i filebeat-7.6.0 -q '{"match_phrase":{"event.type":"authentication_failure"}}' '{"match_phrase":{"host.hostname":"my-server"}}' -a "user.name" -w 10 -c 20 -d -p7d
OK: 9 results found in last 7d. See details below.
 - hacker found 6 times
 - remi found 3 times
|'total_values'=9; 'hacker'=6;10;20; 'remi'=3;10;20;
```

## Credits

2020-08-21 Rémi Verchère <remi.verchere@axians.com> - Published under MIT license

---

# check_elasticsearch.py

A Nagios plugin that checks ElasticSearch health status

## Usage

    check_elasticsearch.py [-h] -H HOSTNAME -U USERNAME -P PASSWORD [-p [PORT]] [-s] [-d]

optional arguments:

* `-h, --help`
  show this help message and exit
* `-H HOSTNAME`, `--hostname HOSTNAME`
  Elastic server hostname or IP address
* `-U USERNAME`, `--username USERNAME`
  username
* `-P PASSWORD`, `--password PASSWORD`
  user password
* `-p [PORT]`, `--port [PORT]`
  listening port
* `-s`, `--ssl`
  use SSL/TLS layer
* `-d`, `--perfdata`
  enable Nagios perf data

## Credits

2018-10-31 Eric Belhomme <rico-github@ricozome.net> - Published under MIT license
