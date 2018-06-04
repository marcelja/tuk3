import os
from threading import Thread
from cursor import Cursor
import geopy.distance


SCHEMA_NAME = 'TUK3_TS_MJ'
THREADS = 8
TIME_INTERVAL_THRESHOLD = 60


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
        # filename = 'distance-{}-{}.csv'.format(begin, end)
        print('Starting thread from {} to {}'.format(begin, end))

        counter = begin
        while counter <= end:
            current_id = ids[counter][0]

            # print('Working on id {}'.format(current_id))
            cursor.execute('select lon, lat, timestamp from shenzhen_clean where id={} order by timestamp'.format(current_id))
            data = cursor.fetchall()

            # try:
            delete = clean_records(data, current_id)
            if delete:
                print("id removed: {}".format(current_id))
            # except:
                # print(current_id, "failed")

            if counter % 50 == 0:
                print('worker {}: {}%'.format(begin, round((counter-begin)*100/(end-begin),1)))

            counter += 1
        print('worker {}: 100.0%'.format(begin))


def clean_records(records_per_tid, current_id):
    _too_high_interval(records_per_tid, current_id)
    # _remove_outliers(records_per_tid)


# def _remove_outliers(records):
#     old_point = (records[0][1], records[0][0])
#     old_timestamp = records[0][2]
#     # for record in records[1:]:





# def _calculate_speed(last_point, current_point):
#     return geopy.distance.vincenty(last_point, current_point).km


def _too_high_interval(records, current_id):
    old_timestamp = records[0][2]
    diff_sum = 0
    for record in records[1:]:
        diff_sum = record[2] - old_timestamp
        old_timestamp = record[2]
    avg_diff = (diff_sum.total_seconds() / len(records))

    if avg_diff > TIME_INTERVAL_THRESHOLD:
        print('AVG time interval for id {} is {} seconds, deleting'.format(current_id, avg_diff))
        return True


if __name__ == '__main__':
    main()
