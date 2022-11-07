import influxdb_client, os, time
from influxdb_client import Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from cloud_utils.influx_config import TOKEN
from datetime import datetime


def get_client():
    org = "av2558@gmail.com"
    url = "https://us-central1-1.gcp.cloud2.influxdata.com"
    client = influxdb_client.InfluxDBClient(url=url, token=TOKEN, org=org)
    return client


def write_point(bucket: str, point: dict):
    client = get_client()
    write_api = client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket, 'av2558@gmail.com', point)


if __name__ == '__main__':
    import pandas as pd
    from datetime import datetime
    import pytz

    finviz_file = r"C:\Users\avass\Downloads\finviz_data.parquet"
    df = pd.read_parquet(finviz_file)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['time'] = df['time'].map(lambda x: datetime.fromtimestamp(x))
    # df.set_index('time', inplace=True)
    finviz_dicts = df.to_dict('records')
    points = []
    for data_point in finviz_dicts:
        symbol = data_point['symbol']
        time = data_point['time']
        data_point.pop('symbol')
        data_point.pop('time')
        points.append({'measurement': 'finviz_data',
                       'tags': {'symbol': symbol},
                       'fields': data_point,
                       'time': time})

    client = get_client()
    write_api = client.write_api(write_options=SYNCHRONOUS)
    # write_api.write("test",
    #                 "av2558@gmail.com",
    #                 points)
    # write_api.write("test",
    #                 "av2558@gmail.com",
    #                 record=df,
    #                 data_frame_measurement_name='finviz_data',
    #                 data_frame_tag_columns=['symbol'])
    for p in points:
        write_api.write('test', 'av2558@gmail.com', p)




