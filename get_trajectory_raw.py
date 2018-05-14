import os
import sys
from datetime import datetime
from cursor import Cursor


SCHEMA_NAME = 'TUK3_TS_MJ'
TID = None


def main():
    global TID

    if (len(sys.argv) != 2):
        raise ValueError('Please provide the trajectory ID as first argument!')
    TID = int(sys.argv[1])

    get_trajectory()


def get_trajectory():
    with Cursor(SCHEMA_NAME) as cursor:
        cursor.execute('SELECT * FROM TUK3_TS_MJ.SHENZHEN WHERE ID={} ORDER BY TIMESTAMP'.format(TID))
        points = cursor.fetchall()
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


if __name__ == '__main__':
    main()
