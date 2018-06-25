import time
import os
from threading import Thread
from cursor import Cursor


SCHEMA_NAME = 'TUK3_TS_MJ'
THREADS = 8
# FRAME_DURATION = 15
POINTS_PER_FRAME_GROUP = 40


def main():
    ids = _get_ids()

    create_csvs(15, 'ts_avg', ids)
    create_csvs(15, 'avg', ids)
    create_csvs(15, 'ts_min', ids)
    create_csvs(15, 'min', ids)
    create_csvs(30, 'ts_avg', ids)
    create_csvs(30, 'avg', ids)
    create_csvs(30, 'ts_min', ids)
    create_csvs(30, 'min', ids)


def create_csvs(frame_duration, procedure, ids):
    directory = 'frame_format_' + str(frame_duration) + '_' + procedure
    if not os.path.exists(directory):
        os.makedirs(directory)

    start = time.time()
    _start_threads(ids, frame_duration, procedure, directory)
    end = time.time()
    elapsed = end - start
    print('elapsed time: {} for {}'.format(elapsed, directory))


def _get_ids():
    with Cursor(SCHEMA_NAME) as cursor:
        cursor.execute('select distinct id from "SHENZHEN_CLEAN" order by id')
        ids = cursor.fetchall()
        return ids


def _start_threads(ids, frame_duration, procedure, directory):
    ids_per_thread = len(ids) / THREADS
    threads = []
    for i in range(THREADS):
        id_offset_begin = int(i * ids_per_thread)
        id_offset_end = int(i * ids_per_thread + ids_per_thread - 1)
        thread = Thread(target=worker_thread, args=(ids, id_offset_begin, id_offset_end,
                                                    frame_duration, procedure, directory))
        threads.append(thread)
        thread.start()
    [t.join() for t in threads]


def worker_thread(ids, begin, end, frame_duration, procedure, directory):
    with Cursor(SCHEMA_NAME) as cursor:
        filename = '{}/frame-{}-{}.csv'.format(directory, begin, end)
        time_counter = 0
        while begin <= end:
            # Result is tuple
            current_id = ids[begin][0]
            # print('Working on id {}'.format(current_id))
            starttime = time.time()
            cursor.execute('call data_for_id_speed_occupancy_{}({}, {}, {}, ?)'.format(procedure,
                                                                                       current_id,
                                                                                       frame_duration,
                                                                                       POINTS_PER_FRAME_GROUP))
            endtime = time.time()
            time_counter += endtime - starttime
            data = cursor.fetchall()

            fgcid = -1
            ifx = 0
            ify = 0

            line = []
            counter = 0
            # Row layout is: LON, LAT, FGCID, FRAME, OCCUPANCY, SPEED
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
                        line.append('')
                        line.append('')
                        counter += 1

                line.append(str(round(row[0] - ifx, 6)))
                line.append(str(round(row[1] - ify, 6)))
                line.append(str(row[4]))
                line.append(str(row[5]))
                counter += 1

            _write_line_to_file(_fill_line(line), filename)
            begin += 1
        print('HANA time: {}'.format(time_counter, directory))


def _fill_line(line):
    """Add missing information at the end of a time frame to the line."""
    # Length must be 164: TID, FGCID, IFX, IFY, 4 * 10 * (PFiPX, PFjPY, occupancy, speed)
    while len(line) < 164:
        line.append('')
        line.append('')
        line.append('')
        line.append('')
    return line


def _write_line_to_file(line, filename):
    joined = ",".join(line)
    with open(filename, 'a') as file:
        file.write(joined)
        file.write(os.linesep)


if __name__ == '__main__':
    main()
