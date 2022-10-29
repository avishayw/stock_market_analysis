import influxdb_client, os, time
from influxdb_client import Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb import InfluxDBClient
from cloud_utils.influx_config import TOKEN


def get_client():
    org = "av2558@gmail.com"
    url = "https://us-central1-1.gcp.cloud2.influxdata.com"
    client = influxdb_client.InfluxDBClient(url=url, token=TOKEN, org=org)
    return client


if __name__ == '__main__':

    client = get_client()
    query_api = client.query_api()
    query = """select * from stock_data"""
    result = query_api.query(org="av2558@gmail.com", query=query)


