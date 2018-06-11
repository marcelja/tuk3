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
        cursor.execute('SELECT TID,FGCID,IFX,IFY,PF0PX,PF0PY,PF1PX,PF1PY,PF2PX,PF2PY,PF3PX,PF3PY,PF4PX,PF4PY,PF5PX,PF5PY,PF6PX,PF6PY,PF7PX,PF7PY,PF8PX,PF8PY,PF9PX,PF9PY,PF10PX,PF10PY,PF11PX,PF11PY,PF12PX,PF12PY,PF13PX,PF13PY,PF14PX,PF14PY,PF15PX,PF15PY,PF16PX,PF16PY,PF17PX,PF17PY,PF18PX,PF18PY,PF19PX,PF19PY,PF20PX,PF20PY,PF21PX,PF21PY,PF22PX,PF22PY,PF23PX,PF23PY,PF24PX,PF24PY,PF25PX,PF25PY,PF26PX,PF26PY,PF27PX,PF27PY,PF28PX,PF28PY,PF29PX,PF29PY,PF30PX,PF30PY,PF31PX,PF31PY,PF32PX,PF32PY,PF33PX,PF33PY,PF34PX,PF34PY,PF35PX,PF35PY,PF36PX,PF36PY,PF37PX,PF37PY,PF38PX,PF38PY,PF39PX,PF39PY \
            FROM TUK3_TS_MJ.FRAME_FORMAT_30 WHERE TID={} ORDER BY FGCID'.format(TID))
            # FROM TUK3_TS_MJ.FRAME_FORMAT_30_AVG WHERE TID={} ORDER BY FGCID'.format(TID))
        framegroups = cursor.fetchall()
    decode_framegroups(framegroups)


def decode_framegroups(framegoups):
    with open('{}_frameformat_30.csv'.format(TID), 'w') as file:
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
    pf_index = 4 + 2 * index
    timestamp = framegroup_if[2] + (index + 1) * 30
    if (framegroup[pf_index] is not None and framegroup[pf_index + 1] is not None):
        lat = framegroup_if[0] + framegroup[pf_index + 1]
        lon = framegroup_if[1] + framegroup[pf_index]
        return (lat, lon, timestamp)
    else:
        return None


if __name__ == '__main__':
    main()