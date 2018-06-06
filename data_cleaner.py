import os
from threading import Thread
from cursor import Cursor
import geopy.distance


SCHEMA_NAME = 'TUK3_TS_MJ'
THREADS = 1
TIME_INTERVAL_THRESHOLD = 90


def main():
    ids = _get_ids()
    _start_threads(ids)


def _get_ids():
    with Cursor(SCHEMA_NAME) as cursor:
        cursor.execute('select distinct id from shenzhen_clean')
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
        # while counter <= end:
        while counter <= 1:
        # while counter <= 20:
            current_id = ids[counter][0]

            current_id = 22323

            cursor.execute('select lon, lat, timestamp, speed from shenzhen_clean where id={} order by timestamp'.format(current_id))
            data = cursor.fetchall()

            clean_records(data, current_id)

            if counter % 50 == 0:
                print('worker {}: {}%'.format(begin, round((counter-begin)*100/(end-begin),1)))

            counter += 1
        print('worker {}: 100.0%'.format(begin))


def clean_records(records_per_tid, current_id):
    # _too_high_interval(records_per_tid, current_id)
    _remove_outliers(records_per_tid, current_id)


def _remove_outliers(records, current_id):
    old_point = (records[0][1], records[0][0])
    old_timestamp = records[0][2]
    outliers = 0

    for idx, record in enumerate(records[1:]):
        speed = _calculate_speed(old_point,
                                 (record[1], record[0]),
                                 old_timestamp,
                                 record[2])
        if speed > 150:
            # This needs to be refactored, not working properly
            outliers += 1
            print("outlier with id {} and timestamp {}, speed {}"
                  .format(current_id, record[2], record[3]))
            # Calc speed to next point
            sp = _calculate_speed(old_point,
                                  (records[idx + 2][1], records[idx + 2][0]),
                                  old_timestamp,
                                  records[idx + 2][2])

            if sp < 150:
                # TODO: really delete entry
                print("delete record with id {} and timestamp {}, speed {}"
                      .format(current_id, record[2], record[3]))
        old_point = (record[1], record[0])
        old_timestamp = record[2]
    print("ID {} has {} outliers".format(current_id, outliers))


def _too_high_interval(records, current_id):
    old_timestamp = records[0][2]
    diff_sum = 0
    for idx, record in enumerate(records[1:]):
        difference = _time_diff(old_timestamp, record[2])
        # Next timestamp after 2.5 minutes
        if difference > 150:
            distance = _calculate_distance((records[idx][1], records[idx][0]),
                                           (record[1], record[0]))
            if distance > 0.25:
                # Car is moving but is not sending information regularly
                # Otherwise car is parking. That should be fine :)
                diff_sum = diff_sum + difference
        else:
            diff_sum = diff_sum + difference
        old_timestamp = record[2]
    avg_diff = diff_sum / len(records)

    if avg_diff > TIME_INTERVAL_THRESHOLD:
        # TODO: really delete entry
        print('AVG time interval for id {} is {} seconds, deleting'.format(current_id, avg_diff))


def _calculate_speed(last_point,
                     current_point,
                     last_timestamp,
                     current_timestamp):
    distance = _calculate_distance(last_point, current_point)
    time_difference = _time_diff(last_timestamp, current_timestamp) / 3600
    return distance / time_difference if time_difference != 0.0 else 9999999999


def _calculate_distance(last_point, current_point):
    return geopy.distance.vincenty(last_point, current_point).km


def _time_diff(start, end):
    return (end - start).total_seconds()


if __name__ == '__main__':
    main()
