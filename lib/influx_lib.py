import logging
from dotenv import load_dotenv

import os
from influxdb_client_3 import (
    InfluxDBClient3, InfluxDBError, Point, WritePrecision,
    WriteOptions, write_client_options)


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)


host = os.getenv("INFLUX_HOST")
token = os.getenv("INFLUX_TOKEN")
database = os.getenv("INFLUX_DATABASE")


def write_influx(measurement, fileds:dict, tags:dict):
    point = Point(measurement)
    for key, value in fileds.items():
        point.tag(key, value)
    for key, value in tags.items():
        point.field(key, value)

    def success(self, data: str):
        logging.info(f"Successfully wrote batch: data: {data}")

    def error(self, data: str, exception: InfluxDBError):
        logging.error(f"Failed writing batch: data: {data} due: {exception}")

    def retry(self, data: str, exception: InfluxDBError):
        logging.warning(f"Retrying to write batch: data: {data} due: {exception}")

    write_options = WriteOptions(batch_size=500,
                                flush_interval=10_000,
                                jitter_interval=2_000,
                                retry_interval=5_000,
                                max_retries=5,
                                max_retry_delay=30_000,
                                exponential_base=2)

    wco = write_client_options(success_callback=success,
                            error_callback=error,
                            retry_callback=retry,
                            write_options=write_options)

    with InfluxDBClient3(host=host,
                        token=token,
                        database=database,
                        write_client_options=wco) as client:
        client.write(record=[point], write_precision='s')

if __name__ == "__main__":
    pass