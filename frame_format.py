import pyhdb
import socket
import logging
import os
from threading import Thread


HANA_USER = None
HANA_PWD = None
SCHEMA_NAME = 'TUK3_TS_MJ'
THREADS = 8


def main():
    global HANA_USER, HANA_PWD
    HANA_USER = os.environ.get('HANA_USER')
    HANA_PWD = os.environ.get('HANA_PWD')
    if not HANA_PWD and not HANA_USER:
        raise EnvironmentError('Please provide user and password as environment variables (HANA_USER, HANA_PWD)!')
    ids = _get_ids()
    _start_threads(ids)


def _get_ids():
    cursor = _get_cursor()
    cursor.execute('select distinct id from "TAXI"."SHENZHEN"')
    ids = cursor.fetchall()
    cursor.connection.close()
    return ids


def _start_threads(ids):
    ids_per_thread = len(ids) / THREADS
    threads = []
    for i in range(THREADS):
        id_offset_begin = int(i * ids_per_thread)
        id_offset_end = int(i * ids_per_thread + ids_per_thread - 1)
        thread = Thread(target=worker_thread, args=(ids, id_offset_begin, id_offset_end))
        threads.append(thread)
        thread.start()
    [t.join() for t in threads]


def worker_thread(ids, begin, end):
    cursor = _get_cursor()
    filename = 'frame-{}-{}.csv'.format(begin, end)
    while begin <= end:
        # Result is tuple
        current_id = ids[begin][0]
        print('Working on id {}'.format(current_id))
        cursor.execute('call data_for_id({}, ?)'.format(current_id))
        data = cursor.fetchall()

        fgcid = -1
        ifx = 0
        ify = 0

        line = []
        counter = 0
        # Row layout is: LON, LAT, FGCID, FRAME
        for row in data:
            if row[2] != fgcid:
                if fgcid != -1:
                    _write_line_to_file(_fill_line(line), filename)
                fgcid = row[2]
                ifx = row[0]
                ify = row[1]
                counter = 0
                line = []
                line.append(str(current_id))
                line.append(str(fgcid))
                line.append(str(ifx))
                line.append(str(ify))

            # Check if data is available
            if counter < row[3]:
                while counter < row[3]:
                    line.append('')
                    line.append('')
                    counter += 1

            line.append(str(round(ifx - row[0], 6)))
            line.append(str(round(ify - row[1], 6)))
            counter += 1

        _write_line_to_file(_fill_line(line), filename)
        begin += 1

    cursor.connection.close()


def _fill_line(line):
    """Add missing information at the end of a time frame to the line."""
    # Length must be 244: TID, FGCID, IFX, IFY, 2*120
    while len(line) < 244:
        line.append('')
        line.append('')
    return line


def _write_line_to_file(line, filename):
    joined = ",".join(line)
    with open(filename, 'a') as file:
        file.write(joined)
        file.write(os.linesep)


def _get_cursor():
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
