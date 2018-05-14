import os
import sys
import json
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
        cursor.execute('SELECT * FROM TUK3_TS_MJ.KEY_VALUE WHERE ID={}'.format(TID))
        trajectory = cursor.fetchone()
        decode_trajectory(trajectory)


def decode_trajectory(trajectory):
    with open('{}_key_value.csv'.format(TID), 'w') as file:
        file.write('latitude,longitude,timestamp')
        file.write(os.linesep)
        trajectory[1].read()
        points = json.loads(str(trajectory[1]))
        for point in points:
            file.write(','.join(str(value) for value in get_point(point)))
            file.write(os.linesep)


def get_point(point):
    print(point)
    lat = point[1]
    lon = point[2]
    date_time = datetime.strptime(point[0], '%Y-%m-%d %H:%M:%S')
    timestamp = date_time.hour * 60 * 60 + date_time.minute * 60 + date_time.second

    return (lat, lon, timestamp)


if __name__ == '__main__':
    main()
