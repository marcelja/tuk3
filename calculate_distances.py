import os
from threading import Thread
from cursor import Cursor
import geopy.distance


SCHEMA_NAME = 'TUK3_TS_MJ'
THREADS = 8


def main():
    ids = _get_ids()
    _start_threads(ids)


def _get_ids():
    with Cursor(SCHEMA_NAME) as cursor:
        cursor.execute('select distinct id from "TAXI"."SHENZHEN"')
        ids = cursor.fetchall()
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
    with Cursor(SCHEMA_NAME) as cursor:
        filename = 'distance-{}-{}.csv'.format(begin, end)
        print('Starting thread from {} to {}'.format(begin, end))

        counter = begin
        while counter <= end:
            current_id = ids[counter][0]

            # print('Working on id {}'.format(current_id))
            cursor.execute('select seconds, lon, lat, occupancy from shenzhen_seconds where id={} order by seconds'.format(current_id))
            data = cursor.fetchall()
            _calculate_total_distance(data, current_id, cursor)

            if counter % 50 == 0:
                print('worker {}: {}%'.format(begin, round((counter-begin)/(end-begin),1)))

            counter += 1


def _calculate_total_distance(data, current_id, cursor):
    occupancy = 0
    current_distance = 0
    last_point = None

    for row in data:
        current_point = (row[2], row[1])

        if occupancy != row[3]:
            occupancy = row[3]

            # The taxi ride has ended
            if occupancy == 0:
                _insert_distance(current_id, current_distance, start_time, row[0], cursor)
                current_distance = 0
                start_time = None
            # New taxi ride starting
            else:
                start_time = row[0]

        elif occupancy == 1:
            current_distance += _calculate_distance(last_point, current_point)
        last_point = current_point


def _calculate_distance(last_point, current_point):
    return geopy.distance.vincenty(last_point, current_point).km


def _insert_distance(tid, distance, start_time, end_time, cursor):
    cursor.execute('insert into distances values ({}, {}, {}, {})'.format(tid, round(distance, 2), start_time, end_time))


if __name__ == '__main__':
    main()
