import pyhdb
import os
import sys

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
    cursor.execute('SELECT * FROM TUK3_TS_MJ.FRAMEFORMAT_NEW WHERE TID={} ORDER BY FGCID'.format(TID))
    framegroups = cursor.fetchall()
    cursor.connection.close()
    decode_framegroups(framegroups)

def decode_framegroups(framegoups):
    with open('{}_frameformat.csv'.format(TID), 'w') as file:
        file.write('latitude,longitude,timestamp')
        file.write(os.linesep)
        for group in framegoups:
            file.write(','.join(str(value) for value in get_if_coord(group)))
            file.write(os.linesep)
            for i in range((len(group) - 4) / 2):
                pf_coord = get_pf_coord(group, i)
                if (pf_coord is not None):
                    file.write(','.join(str(value) for value in pf_coord))
                    file.write(os.linesep)

def get_if_coord(framegroup):
    lat = framegroup[3]
    lon = framegroup[2]
    timestamp = framegroup[1] * 60 * 60

    return (lat, lon, timestamp)

def get_pf_coord(framegroup, index):
    frame_if = get_if_coord(framegroup)
    pf_index = 4 + index
    timestamp = frame_if[2] + (index + 1) * 30
    if (framegroup[pf_index] is not None and framegroup[pf_index + 1] is not None):
        lat = frame_if[0] + framegroup[pf_index + 1]
        lon = frame_if[1] + framegroup[pf_index]
        return (lat, lon, timestamp)
    else:
        return None


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
