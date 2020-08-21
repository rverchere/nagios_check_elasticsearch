#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: expandtab sw=4 ts=4:
'''
Nagios plugin that makes ElasticSearch queries
2020-08-21 Rémi Verchère <remi.verchere@axians.com> - Initial work
Published under MIT license
'''

import sys
import argparse
import json
from pprint import pprint
from elasticsearch import Elasticsearch

__author__ = "Rémi Verchère"
__contact__ = "remi.vercherea@axians.com"
__license__ = "MIT"
__version__ = "0.0.1"

def queryElasticsearch(esHost, esUser, esPasswd, esIndex, esQuery, esPeriod, esAggs):

    # Manage time, format like now-15m
    gte = "now-{}".format(esPeriod)

    # Default elasticsearch query, which will be enhanced later using esQuery list
    esquery = {
      "size": 0,
      "query": {
        "bool": {
          "filter": [
            {
              "range": {
                "@timestamp": {
                  "gte": gte,
                  "lte": "now",
                  "format": "strict_date_optional_time"
                }
              }
            }
          ]
        }
      },
      "aggs": {
        "aggregates": {
          "terms": {
            "field": esAggs
          }
        }
      }
    }
    # filters are added here
    # -q '{"match_phrase":{"event.type":"authentication_failure"}}' '{"match_phrase":{"host.hostname":"S405LIAEOLH4"}}'
    for query in esQuery:
        for q in query:
            filter_string = json.loads(q)
            esquery["query"]["bool"]["filter"].append(filter_string)

    try:
        es = Elasticsearch(esHost,http_auth=(esUser,esPasswd))
        results = es.search(index=esIndex,body=esquery)
    except Exception as e:
        print("Cannot connect to Elasticsearch host: {}".format(e))
        sys.exit(3)

    return results


##### Main starts here
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Nagios check for Elasticsearch queries',
        epilog="version {}".format(__version__))
    parser.add_argument('-H', '--hostname', type=str, help='hostname or IP address of Elasticsearch server', required=True)
    parser.add_argument('-U', '--username', type=str, help='username', required=True)
    parser.add_argument('-P', '--password', type=str, help='user password', required=True)
    parser.add_argument('-i', '--index', type=str, help='index where are performed the requests', required=True)
    parser.add_argument('-q', '--query', action='append', nargs='+', help='part of the query (i.e : {"match_phrase":{"event.type":"authentication_failure"}})', required=True)
    parser.add_argument('-a', '--aggs', type=str, help='aggregation terms', default="")
    parser.add_argument('-p', '--period', type=str, help='period from now (i.e. 15m)', default="1d")
    parser.add_argument('-w', '--warning', type=int, nargs='?', help='warning trigger for total records', default=5)
    parser.add_argument('-c', '--critical', type=int, nargs='?', help='critical trigger for total records', default=10)
    parser.add_argument('-d', '--perfdata', help='enable Nagios perf data', action='store_true')

    args = parser.parse_args()

    # default values
    retcode = 3
    message = "UNKNOWN: Cannot retrieve Elasticsearch results"

    results = queryElasticsearch(args.hostname, args.username, args.password, args.index, args.query, args.period, args.aggs)

    # Manage records found. if aggregations, get the value per aggr
    aggs = results['aggregations']['aggregates']['buckets']
    total = results['hits']['total']['value']
    records = []
    if aggs:
      for agg in aggs:
        records.append(agg['doc_count'])
    else:
        records.append(total)

    for record in records:
        if record >= args.critical:
            retcode = 2
            message = "CRITICAL:"
            break
        elif record >= args.warning:
            retcode = 1
            message = "WARNING:"
            break
        elif record >= 0:
            retcode = 0
            message = "OK:"
            break

    if total >= 0:
        message += " {} results found in last {}.".format(total, args.period)
    else:
        message = "UNKNOWN: Invalid results"


    # If aggs, add informationa
    if aggs:
        message += " See details below."
        for agg in aggs:
            message += "\n - {} found {} times".format(agg['key'],agg['doc_count'])

    if args.perfdata:
        if aggs:
            message += "\n|'total_values'={};".format(total)
            for agg in aggs:
                message += " '{}'={};{};{};".format(agg['key'],agg['doc_count'],args.warning, args.critical)
        else:
            message += "\n|'total_values'={};{};{};".format(total, args.warning, args.critical)

    # Finally, print all information
    print(message)
    sys.exit(retcode)
