import os
import sys
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
        cursor.execute('SELECT * FROM TUK3_TS_MJ.FRAMEFORMAT_NEW WHERE TID={} ORDER BY FGCID'.format(TID))
        framegroups = cursor.fetchall()
    decode_framegroups(framegroups)


def decode_framegroups(framegoups):
    with open('{}_frameformat.csv'.format(TID), 'w') as file:
        file.write('latitude,longitude,timestamp')
        file.write(os.linesep)
        for group in framegoups:
            if_coord = get_if_coord(group)
            file.write(','.join(str(value) for value in if_coord))
            file.write(os.linesep)
            for i in range(int((len(group) - 4) / 2)):
                pf_coord = get_pf_coord(group, i, if_coord)
                if (pf_coord is not None):
                    file.write(','.join(str(value) for value in pf_coord))
                    file.write(os.linesep)


def get_if_coord(framegroup):
    lat = framegroup[3]
    lon = framegroup[2]
    timestamp = framegroup[1] * 60 * 60

    return (lat, lon, timestamp)


def get_pf_coord(framegroup, index, framegroup_if):
    pf_index = 4 + index
    timestamp = framegroup_if[2] + (index + 1) * 30
    if (framegroup[pf_index] is not None and framegroup[pf_index + 1] is not None):
        lat = framegroup_if[0] + framegroup[pf_index + 1]
        lon = framegroup_if[1] + framegroup[pf_index]
        return (lat, lon, timestamp)
    else:
        return None


if __name__ == '__main__':
    main()
