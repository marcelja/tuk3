import os
import json
import datetime
from threading import Thread
from cursor import Cursor

SCHEMA_NAME = 'TUK3_TS_MJ'
THREADS = 8


def main():
    ids = get_ids()
    start_threads(ids)


def get_ids():
    with Cursor(SCHEMA_NAME) as cursor:
        cursor.execute('select distinct id from SHENZHEN')
        ids = cursor.fetchall()
        return ids


def start_threads(ids):
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
        filename = 'kv-{}-{}.csv'.format(begin, end)
        while begin <= end:
            # Result is tuple
            current_id = ids[begin][0]
            print('Working on id {}'.format(current_id))
            cursor.execute('SELECT * FROM SHENZHEN WHERE ID={} ORDER BY TIMESTAMP'.format(current_id))
            data = cursor.fetchall()
            
            line = []
            line.append(str(current_id))
            trajectory = []
            start_time = data[0][1]
            end_time = data[0][1]
            mbr = [
                data[0][3],
                data[0][2],
                data[0][3],
                data[0][2]
            ]
            for row in data:
                timestamp = row[1]
                lat = row[3]
                lon = row[2]
                trajectory.append([
                    str(timestamp),
                    lat,
                    lon 
                ])
                if (timestamp < start_time):
                    start_time = timestamp
                if timestamp > end_time:
                    end_time = timestamp
                if lat < mbr[0]:
                    mbr[0] = lat
                if lat > mbr[2]:
                    mbr[2] = lat
                if lon < mbr[1]:
                    mbr[1] = lon
                if lon > mbr[3]:
                    mbr[3] = lon

            line.append(json.dumps(trajectory))
            line.append(str(start_time))
            line.append(str(end_time))
            line.append(json.dumps(mbr))
            write_line_to_file(line, filename)
            begin += 1

def write_line_to_file(line, filename):
    joined = "|".join(line)
    with open(filename, 'a') as file:
        file.write(joined)
        file.write(os.linesep)

if __name__ == '__main__':
    main()
