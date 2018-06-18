from cursor import Cursor
from flask import Flask, render_template, Response
import json
import datetime
import time
import re

app = Flask(__name__)

SCHEMA_NAME = 'TUK3_TS_MJ'
FRAME_SIZE = 15  # seconds
FRAME_GROUP_SIZE = 10  # minutes


@app.route('/')
def index():
    return render_template('map.html')

@app.route('/compare')
def compare():
    return render_template('compare.html')


@app.route('/trajectory_point/<int:tid>')
def trajectory_point(tid):
    # Must be in range 22223 <= TID <= 36950
    with Cursor(SCHEMA_NAME) as cursor:
        query = '''select lat, lon, timestamp
                   from "TAXI"."SHENZHEN"
                   where id = {}
                   order by timestamp'''.format(tid)
        cursor.execute(query)
        return Response(json.dumps(cursor.fetchall(),
                                   default=_convert_timestamp, separators=(',', ':')),
                        mimetype='application/json')


@app.route('/trajectory_frame/<int:tid>')
def trajectory_frame(tid):
    # Must be in range 22223 <= TID <= 36950
    with Cursor(SCHEMA_NAME) as cursor:
        # Layout: tid, fgcid, ifx, ify, pf0px, pf0py, ...
        query = 'select tid, fgcid, ifx, ify'
        for i in range(40):
            query += ', pf0px, pf1px'
        query += ''' from "TUK3_TS_MJ"."FRAME_FORMAT_15"
                   where tid = {}
                   order by fgcid'''.format(tid)
        cursor.execute(query)
        query_result = cursor.fetchall()
        result = []
        for framegroup in query_result:
            ifx = framegroup[2]
            ify = framegroup[3]
            for frame in range(int(60 / FRAME_SIZE) * FRAME_GROUP_SIZE):
                index = 4 + 2 * frame
                if framegroup[index] is not None:
                    result.append([framegroup[index + 1] + ify,
                                   framegroup[index] + ifx,
                                   _get_timestamp(framegroup[1], frame)])
        return Response(json.dumps(result, separators=(',', ':')), mimetype='application/json')


@app.route('/trajectory_keyvalue/<int:tid>')
def trajectory_keyvalue(tid):
    # Must be in range 22223 <= TID <= 36950
    with Cursor(SCHEMA_NAME) as cursor:
        query = '''select obj from "TUK3_TS_MJ"."KEY_VALUE"
                   where id = {}'''.format(tid)
        cursor.execute(query)
        result_tuple = cursor.fetchone()
        # tuple contains only one selected value
        trajectory_object = result_tuple[0].read()
        return Response(json.dumps(json.loads(trajectory_object), separators=(',', ':')),
                        mimetype='application/json')


@app.route('/timeframe/<int:fgcid>/<int:frame>')
def timeframe(fgcid, frame):
    with Cursor(SCHEMA_NAME) as cursor:
        lat = 'PF{}PX'.format(frame)
        lon = 'PF{}PY'.format(frame)
        query = '''select {0} + ify as lat, {1} + ifx as lon
                   from "TUK3_TS_MJ"."FRAME_FORMAT_15"
                   where fgcid = {2}
                   and {0} is not NULL'''.format(lat, lon, fgcid)

        cursor.execute(query)
        return Response(json.dumps(cursor.fetchall(), separators=(',', ':')), mimetype='application/json')


@app.route('/timeframe_granularity/<int:fgcid>/<int:frame>/<int:granularity>')
def timeframe_granularity(fgcid, frame, granularity):
    # Granularity is supposed to be >= 0 and < 7
    with Cursor(SCHEMA_NAME) as cursor:
        lat = 'PF{}PX'.format(frame)
        lon = 'PF{}PY'.format(frame)
        query = '''select lat, lon, count(*) as weight from (
                            select round({0} + ify, {1}) as lat,
                                   round({2} + ifx, {1}) as lon
                            from "TUK3_TS_MJ"."FRAME_FORMAT_15"
                            where fgcid = {3}
                            and {0} is not NULL)
                        group by lat, lon'''.format(lat, granularity, lon, fgcid)

        cursor.execute(query)
        return Response(json.dumps(cursor.fetchall(), separators=(',', ':')), mimetype='application/json')

@app.route('/route/<int:tid>')
def route_information(tid):
    with Cursor(SCHEMA_NAME) as cursor:
        query = '''select timestamp,lon,lat,occupancy
                        from shenzhen_clean
                        where id='{}' order by timestamp
                '''.format(tid)

        cursor.execute(query)
        result = cursor.fetchall()
        return Response(json.dumps([('{0.hour:02d}:{0.minute:02d}:{0.second:02d}'.format(x[0]),x[1],x[2],x[3]) for x in result], separators=(',', ':')), mimetype='application/json')

@app.route('/key_value/<int:hour>')
def key_value(hour):
    with Cursor(SCHEMA_NAME) as cursor:
        results = []
        query = '''select OBJ from KEY_VALUE where 
                        ST <= to_timestamp('01.01.0001 {0}:00:00', 'dd.mm.yyyy hh24:mi:ss') 
                        AND ET >= to_timestamp('01.01.0001 {0}:00:00', 'dd.mm.yyyy hh24:mi:ss')
                '''.format(hour)
        cursor.execute(query)
        # all = cursor.fetchall()
        # return str(all[0][0].read(all[0][0].length))

        regex = r'.*\["\d{4}-\d{2}-\d{2} ' + '{0:0>2}'.format(hour) + ':00:[0-5][0-9]",(\d{2,3}\.\d{1,6}),(\d{2,3}\.\d{1,6})\].*'
        print("matching {}".format(regex))
        for trajectory in cursor.fetchall():
            full_trajectory = trajectory[0].read(trajectory[0].length)
            match = re.match(regex, full_trajectory, re.M|re.I)
            if match:
                results.append([float(match.group(1)), float(match.group(2)), 1])
        print("matched")
        return Response(json.dumps(results, separators=(',', ':')), mimetype='application/json')

@app.route('/changepoints/<mode>/<int:fgcid>/<int:granularity>')
def changepoints(mode, fgcid, granularity):
    with Cursor(SCHEMA_NAME) as cursor:
        results = []

        compare_direction = '>' if mode == 'pickup' else  '<'

        query = '''CALL TUK3_TS_MJ.changepoints_for_framegroup({0}, {1}, '{2}', ?)
                '''.format(fgcid, granularity, compare_direction)
        cursor.execute(query)
        results = cursor.fetchall()

        return Response(json.dumps(results, separators=(',', ':')), mimetype='application/json')

def _convert_timestamp(ts):
    if isinstance(ts, datetime.datetime):
        return str(ts)


def _get_timestamp(fgcid, frame):
    seconds = fgcid * FRAME_GROUP_SIZE * 60 + frame * FRAME_SIZE
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(seconds))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=9001)
