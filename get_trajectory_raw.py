import pyhdb
import os
import sys
from datetime import datetime

HANA_USER = None
HANA_PWD = None
SCHEMA_NAME = 'TUK3_TS_MJ'
TID = None

def main():
    global HANA_USER, HANA_PWD, TID
    HANA_USER = os.environ.get('HANA_USER')
    HANA_PWD = os.environ.get('HANA_PWD')
    if not HANA_PWD and not HANA_USER:
        raise EnvironmentError('Please provide user and password as environment variables (HANA_USER, HANA_PWD)!')

    if (len(sys.argv) != 2):
        raise ValueError('Please provide the trajectory ID as first argument!')
    TID = int(sys.argv[1])

    get_trajectory()

def get_trajectory():
    cursor = get_cursor()
    cursor.execute('SELECT * FROM TUK3_TS_MJ.SHENZHEN WHERE ID={} ORDER BY TIMESTAMP'.format(TID))
    points = cursor.fetchall()
    cursor.connection.close()
    decode_framegroups(points)

def decode_framegroups(points):
    with open('{}_raw.csv'.format(TID), 'w') as file:
        file.write('latitude,longitude,timestamp')
        file.write(os.linesep)
        for point in points:
            file.write(','.join(str(value) for value in get_point(point)))
            file.write(os.linesep)

def get_point(point):
    lat = point[3]
    lon = point[2]
    timestamp = point[1].hour * 60 * 60 + point[1].minute * 60 + point[1].second
   
    return (lat, lon, timestamp)

def get_cursor():
    try:
        connection = pyhdb.Connection(
            host="side.eaalab.hpi.uni-potsdam.de",
            port=30015,
            user=HANA_USER,
            password=HANA_PWD,
            autocommit=True,
            timeout=None
        )
        connection.connect()
        cursor = connection.cursor()
        cursor.execute('set schema {}'.format(SCHEMA_NAME))
    except socket.gaierror as e:
        logging.error('Database instance is not available!')
        raise e

    return cursor

if __name__ == '__main__':
    main()
