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
                   from shenzhen_clean
                   where id = {}
                   order by timestamp'''.format(tid)
        cursor.execute(query)
        response = {
            "result": cursor.fetchall(),
            "performance": {
                "query": query,
                "sql": get_sql_execution_time(query),
                "python": 0
            }
        }
        return Response(json.dumps(response,
                                default=_convert_timestamp,
                                separators=(',', ':')),
                        mimetype='application/json')

@app.route('/trajectory_keyvalue/<int:tid>')
def trajectory_keyvalue(tid):
    # Must be in range 22223 <= TID <= 36950
    query = '''select obj from "TUK3_TS_MJ"."KEY_VALUE"
               where id = {}'''.format(tid)

    with Cursor(SCHEMA_NAME) as cursor:
        cursor.execute(query)
        result_tuple = cursor.fetchone()
        # tuple contains only one selected value
        start = time.clock()
        trajectory_object = result_tuple[0].read()
        end = time.clock()

    response = {
        "performance": {
            "query": query,
            "sql": get_sql_execution_time(query),
            "python": calc_execution_time(start, end)
        },
        "result": json.loads(trajectory_object)
    }
    return Response(json.dumps(response, separators=(',', ':')),
                    mimetype='application/json')

@app.route('/trajectory_frame/<int:tid>')
def trajectory_frame(tid):
    # Must be in range 22223 <= TID <= 36950
    with Cursor(SCHEMA_NAME) as cursor:
        # Layout: tid, fgcid, ifx, ify, pf0px, pf0py, ...
        query = 'select tid, fgcid, ifx, ify'
        for i in range(40):
            query += ', pf{0}px, pf{0}py'.format(i)
        query += ''' from "TUK3_TS_MJ"."FRAME_FORMAT_15"
                   where tid = {}
                   order by fgcid'''.format(tid)
        cursor.execute(query)
        query_result = cursor.fetchall()
        result = []
        start = time.clock()
        for framegroup in query_result:
            ifx = framegroup[2]
            ify = framegroup[3]
            for frame in range(int(60 / FRAME_SIZE) * FRAME_GROUP_SIZE):
                index = 4 + 2 * frame
                if framegroup[index] is not None:
                    result.append([framegroup[index + 1] + ify,
                                   framegroup[index] + ifx,
                                   _get_timestamp(framegroup[1], frame)])
        end = time.clock()

        response = {
            "performance": {
                "query": query,
                "sql": get_sql_execution_time(query),
                "python": calc_execution_time(start, end)
            },
            "result": result
        }
        return Response(json.dumps(response, separators=(',', ':')), mimetype='application/json')



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


@app.route('/timeframe_granularity/<int:fgcid>/<int:granularity>')
def timeframe_granularity(fgcid, granularity):
    # Granularity is supposed to be >= 0 and < 7
    with Cursor(SCHEMA_NAME) as cursor:
        
        query =  '''select lat, lon, count(*) as weight from (
                        select round(frame_format_15.ify + frame_format_15.pf0py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf0px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf1py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf1px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf2py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf2px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf3py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf3px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf4py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf4px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf5py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf5px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf6py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf6px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf7py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf7px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf8py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf8px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf9py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf9px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf9py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf9px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf10py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf10px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf11py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf11px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf12py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf12px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf13py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf13px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf14py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf14px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf15py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf15px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf16py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf16px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf17py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf17px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf18py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf18px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf19py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf19px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf20py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf20px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf21py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf21px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf22py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf22px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf23py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf23px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf24py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf24px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf25py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf25px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf26py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf26px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf27py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf27px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf28py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf28px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf29py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf29px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf30py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf30px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf31py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf31px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf32py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf32px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf33py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf33px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf34py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf34px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf35py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf35px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf36py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf36px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf37py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf37px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf38py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf38px, {1}) as lon from frame_format_15 where fgcid = {0}
                        union all select round(frame_format_15.ify + frame_format_15.pf39py, {1}) as lat, round(frame_format_15.ifx + frame_format_15.pf39px, {1}) as lon from frame_format_15 where fgcid = {0}
                    )
                    group by lat, lon;
                '''.format(fgcid, granularity)

        cursor.execute(query)
        result = cursor.fetchall()

        response = {
            "performance": {
                "query": query,
                "sql": get_sql_execution_time(query),
                "python": 0
            },
            "result": result
        }
        return Response(json.dumps(response, separators=(',', ':')), mimetype='application/json')

@app.route('/timeframe_granularity_heatmap/<int:fgcid>/<int:granularity>')
def timeframe_granularity_heatmap(fgcid, granularity):
    # Granularity is supposed to be >= 0 and < 7
    with Cursor(SCHEMA_NAME) as cursor:
        query = '''select lat, lon, count(*) as weight from (
                            select round(pf0py + ify, {1}) as lat,
                                   round(pf0px + ifx, {1}) as lon
                            from frame_format_15
                            where fgcid = {0}
                            and pf0py is not NULL)
                        group by lat, lon'''.format(fgcid, granularity)

        cursor.execute(query)
        result = cursor.fetchall()

        response = {
            "performance": {
                "query": query,
                "sql": get_sql_execution_time(query),
                "python": 0
            },
            "result": result
        }
        return Response(json.dumps(response, separators=(',', ':')), mimetype='application/json')

@app.route('/timeframe_granularity_points/<int:fgcid>/<int:granularity>')
def timeframe_granularity_points(fgcid, granularity):
    with Cursor(SCHEMA_NAME) as cursor:
        start = time.clock()
        seconds = fgcid * 10 * 60
        end = time.clock()
        query =  '''SELECT lat, lon, count(*) from (
                    SELECT 
                        round(lat, {2}) as lat, 
                        round(lon, {2}) as lon 
                    FROM shenzhen_clean 
                    WHERE 
                        seconds >= {0} 
                        AND seconds <= {1} 
                        AND lat IS NOT NULL
                ) GROUP BY lat, lon'''.format(seconds, seconds + 15, granularity)

        cursor.execute(query)
        result = cursor.fetchall()

        response = {
            "performance": {
                "query": query,
                "sql": get_sql_execution_time(query),
                "python": calc_execution_time(start, end)
            },
            "result": result
        }
        return Response(json.dumps(response, separators=(',', ':')), mimetype='application/json')

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

        start = time.clock()
        compare_direction = '>' if mode == 'pickup' else  '<'
        end = time.clock()

        query = '''CALL TUK3_TS_MJ.changepoints_for_framegroup({0}, {1}, '{2}', ?)'''.format(fgcid, granularity, compare_direction)
        cursor.execute(query)
        results = cursor.fetchall()

        response = {
            "performance": {
                "query": query,
                "sql": get_sql_execution_time(query.replace("'", "''")),
                "python": calc_execution_time(start, end)
            },
            "result": results
        }
        return Response(json.dumps(response, separators=(',', ':')), mimetype='application/json')

@app.route('/changepoints_points/<mode>/<int:fgcid>/<int:granularity>')
def changepoints_poinnts(mode, fgcid, granularity):
    with Cursor(SCHEMA_NAME) as cursor:
        results = []

        start = time.clock()
        compare_direction = '>' if mode == 'pickup' else  '<'
        framebegin = fgcid * 10 * 60
        framelength = 600
        end = time.clock()

        query = '''CALL TUK3_TS_MJ.changepoints_for_point_format({0}, {1}, {2}, '{3}', ?)'''.format(framebegin, framelength, granularity, compare_direction)
        cursor.execute(query)
        results = cursor.fetchall()

        response = {
            "performance": {
                "query": query,
                "sql": get_sql_execution_time(query.replace("'", "''")),
                "python": calc_execution_time(start, end)
            },
            "result": results
        }
        return Response(json.dumps(response, separators=(',', ':')), mimetype='application/json')

@app.route('/changepoints_points_sorted/<mode>/<int:fgcid>/<int:granularity>')
def changepoints_points_sorted(mode, fgcid, granularity):
    with Cursor(SCHEMA_NAME) as cursor:
        results = []

        start = time.clock()
        compare_direction = '>' if mode == 'pickup' else  '<'
        framebegin = fgcid * 10 * 60
        framelength = 600
        end = time.clock()

        query = '''CALL TUK3_TS_MJ.changepoints_for_point_format_toni({0}, {1}, {2}, '{3}', ?)'''.format(framebegin, framelength, granularity, compare_direction)
        cursor.execute(query)
        results = cursor.fetchall()

        response = {
            "performance": {
                "query": query,
                "sql": get_sql_execution_time(query.replace("'", "''")),
                "python": calc_execution_time(start, end)
            },
            "result": results
        }
        return Response(json.dumps(response, separators=(',', ':')), mimetype='application/json')

@app.route('/profit')
def profit():
    with Cursor(SCHEMA_NAME) as cursor:
        results = []

        query = "SELECT * FROM profit ORDER by profit DESC LIMIT 100;"
        cursor.execute(query)
        results = cursor.fetchall()

        return Response(json.dumps(results, separators=(',', ':')), mimetype='application/json')

@app.route('/profit_manual')
def profit_manual():
    with Cursor(SCHEMA_NAME) as cursor:
        result = []

        query = '''
            select sum_table.id, sum_distance*2.4/1000+(sum_seconds*0.1*48/3600)+11*num_rides as profit, sum_distance*2.4/1000 as profit_distance, sum_seconds*0.1*48/3600 as profit_waiting, 11*num_rides as profit_taxi_start from

            ----- calculate sum of distances and sum of seconds for each id
            (
                select sum(distance) as sum_distance,sum(scnds) as sum_seconds,id from
                (
                select t1.id, t2.seconds-t1.seconds as scnds, power(t1.lat-t2.lat, 2) + power((t1.lon-t2.lon)*cos(t2.lat * 3.14159265 / 180), 2)  as distance from 
                (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted
                order by seconds) t1,
                (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted 
                order by seconds) t2
                where t1.rid = t2.rid-1 and t1.occupancy=1 and t2.occupancy=1 and t1.id=t2.id
                ) group by id order by sum_distance desc
            ) sum_table,

            ----- calculate number of rides
            (
                select t1.id, count(t1.id) as num_rides from 
                (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted
                order by seconds) t1,
                (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted 
                order by seconds) t2
                where t1.rid = t2.rid-1 and t1.occupancy=1 and t2.occupancy=0 and t1.id=t2.id
                group by t1.id
            ) num_rides
            where sum_table.id=num_rides.id
            order by id
        '''.format(id)
        cursor.execute(query)
        result = cursor.fetchall()
        start = time.clock()
        for i in range(len(result)):
            result[i] = list(result[i])
            result[i][3] = float(result[i][3])
        end = time.clock()

        response = {
            "performance": {
                "query": query,
                "sql": get_sql_execution_time(query.replace("'", "''")),
                "python": calc_execution_time(start, end)
            },
            "result": result
        }
        return Response(json.dumps(response, separators=(',', ':')), mimetype='application/json')


@app.route('/profit/<int:id>')
def profit_id(id):
    with Cursor(SCHEMA_NAME) as cursor:
        result = []

        query = '''
            select sum_table.id, sum_distance*2.4/1000+(sum_seconds*0.1*48/3600)+11*num_rides as profit, sum_distance*2.4/1000 as profit_distance, sum_seconds*0.1*48/3600 as profit_waiting, 11*num_rides as profit_taxi_start from

            ----- calculate sum of distances and sum of seconds for each id
            (
                select sum(distance) as sum_distance,sum(scnds) as sum_seconds,id from
                (
                select t1.id, t2.seconds-t1.seconds as scnds, new ST_POINT(t1.lon, t1.lat).st_srid(4326).st_transform(4326).st_distance(  new ST_POINT(t2.lon, t2.lat).st_srid(4326).st_transform(4326)   ) as distance from 
                (select lon,lat,seconds,id,occupancy, ROW_NUMBER() OVER (PARTITION BY id order by seconds) AS row_num from shenzhen_clean
                where id = {0}
                order by seconds) t1,
                (select lon,lat,seconds,id,occupancy, ROW_NUMBER() OVER (PARTITION BY id order by seconds) AS row_num from shenzhen_clean 
                where id = {0}
                order by seconds) t2
                where t1.row_num = t2.row_num-1 and t1.occupancy=1 and t2.occupancy=1 and t1.id=t2.id
                ) group by id order by sum_distance desc
            ) sum_table,

            ----- calculate number of rides
            (
                select t1.id, count(t1.id) as num_rides from 
                (select lon,lat,seconds,id,occupancy, ROW_NUMBER() OVER (PARTITION BY id order by seconds) AS row_num from shenzhen_clean
                where id = {0}
                order by seconds) t1,
                (select lon,lat,seconds,id,occupancy, ROW_NUMBER() OVER (PARTITION BY id order by seconds) AS row_num from shenzhen_clean 
                where id = {0}
                order by seconds) t2
                where t1.row_num = t2.row_num-1 and t1.occupancy=1 and t2.occupancy=0 and t1.id=t2.id
                group by t1.id
            ) num_rides
            where sum_table.id=num_rides.id
            '''.format(id)
        cursor.execute(query)
        result = list(cursor.fetchone())
        result[3] = float(result[3])

        response = {
            "performance": {
                "query": query,
                "sql": get_sql_execution_time(query.replace("'", "''")),
                "python": 0
            },
            "result": result
        }
        return Response(json.dumps(response, separators=(',', ':')), mimetype='application/json')

@app.route('/profit_sorted/<int:id>')
def profit_id_sorted(id):
    with Cursor(SCHEMA_NAME) as cursor:
        result = []

        query = '''
            select sum_table.id, sum_distance*2.4/1000+(sum_seconds*0.1*48/3600)+11*num_rides as profit, sum_distance*2.4/1000 as profit_distance, sum_seconds*0.1*48/3600 as profit_waiting, 11*num_rides as profit_taxi_start from

            ----- calculate sum of distances and sum of seconds for each id
            (
                select sum(distance) as sum_distance,sum(scnds) as sum_seconds,id from
                (
                select t1.id, t2.seconds-t1.seconds as scnds, new ST_POINT(t1.lon, t1.lat).st_srid(4326).st_transform(4326).st_distance(  new ST_POINT(t2.lon, t2.lat).st_srid(4326).st_transform(4326)   ) as distance from 
                (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted
                where id = {0}
                order by seconds) t1,
                (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted 
                where id = {0}
                order by seconds) t2
                where t1.rid = t2.rid-1 and t1.occupancy=1 and t2.occupancy=1 and t1.id=t2.id
                ) group by id order by sum_distance desc
            ) sum_table,

            ----- calculate number of rides
            (
                select t1.id, count(t1.id) as num_rides from 
                (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted
                where id = {0}
                order by seconds) t1,
                (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted 
                where id = {0}
                order by seconds) t2
                where t1.rid = t2.rid-1 and t1.occupancy=1 and t2.occupancy=0 and t1.id=t2.id
                group by t1.id
            ) num_rides
            where sum_table.id=num_rides.id
            '''.format(id)
        cursor.execute(query)
        result = list(cursor.fetchone())
        result[3] = float(result[3])

        response = {
            "performance": {
                "query": query,
                "sql": get_sql_execution_time(query.replace("'", "''")),
                "python": 0
            },
            "result": result
        }
        return Response(json.dumps(response, separators=(',', ':')), mimetype='application/json')

@app.route('/profit_precalculated_st/<int:id>')
def profit_id_precalculated_st(id):
    with Cursor(SCHEMA_NAME) as cursor:
        result = []

        query = '''
            select sum_table.id, sum_distance*2.4/1000+(sum_seconds*0.1*48/3600)+11*num_rides as profit, sum_distance*2.4/1000 as profit_distance, sum_seconds*0.1*48/3600 as profit_waiting, 11*num_rides as profit_taxi_start from

            ----- calculate sum of distances and sum of seconds for each id
            (
                select sum(distance) as sum_distance,sum(scnds) as sum_seconds,id from
                (
                select t1.id, t2.seconds-t1.seconds as scnds, t1.point.st_distance(t2.point) as distance from 
                (select point, seconds,id,occupancy, rid from shenzhen_stpoints
                where id = {0}
                order by seconds) t1,
                (select point, seconds,id,occupancy, rid from shenzhen_stpoints 
                where id = {0}
                order by seconds) t2
                where t1.rid = t2.rid-1 and t1.occupancy=1 and t2.occupancy=1 and t1.id=t2.id
                ) group by id order by sum_distance desc
            ) sum_table,

            ----- calculate number of rides
            (
                select t1.id, count(t1.id) as num_rides from 
                (select point, seconds,id,occupancy, rid from shenzhen_stpoints
                where id = {0}
                order by seconds) t1,
                (select point, seconds,id,occupancy, rid from shenzhen_stpoints 
                where id = {0}
                order by seconds) t2
                where t1.rid = t2.rid-1 and t1.occupancy=1 and t2.occupancy=0 and t1.id=t2.id
                group by t1.id
            ) num_rides
            where sum_table.id=num_rides.id
            '''.format(id)
        cursor.execute(query)
        result = list(cursor.fetchone())
        result[3] = float(result[3])

        response = {
            "performance": {
                "query": query,
                "sql": get_sql_execution_time(query.replace("'", "''")),
                "python": 0
            },
            "result": result
        }
        return Response(json.dumps(response, separators=(',', ':')), mimetype='application/json')

@app.route('/profit_manual/<int:id>')
def profit_id_manual(id):
    with Cursor(SCHEMA_NAME) as cursor:
        result = []

        query = '''
            select sum_table.id, sum_distance*2.4/1000+(sum_seconds*0.1*48/3600)+11*num_rides as profit, sum_distance*2.4/1000 as profit_distance, sum_seconds*0.1*48/3600 as profit_waiting, 11*num_rides as profit_taxi_start from

            ----- calculate sum of distances and sum of seconds for each id
            (
                select sum(distance) as sum_distance,sum(scnds) as sum_seconds,id from
                (
                select t1.id, t2.seconds-t1.seconds as scnds, power(t1.lat-t2.lat, 2) + power((t1.lon-t2.lon)*cos(t2.lat * 3.14159265 / 180), 2)  as distance from 
                (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted
                where id = {0}
                order by seconds) t1,
                (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted 
                where id = {0}
                order by seconds) t2
                where t1.rid = t2.rid-1 and t1.occupancy=1 and t2.occupancy=1 and t1.id=t2.id
                ) group by id order by sum_distance desc
            ) sum_table,

            ----- calculate number of rides
            (
                select t1.id, count(t1.id) as num_rides from 
                (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted
                where id = {0}
                order by seconds) t1,
                (select lon,lat,seconds,id,occupancy, rid from shenzhen_sorted 
                where id = {0}
                order by seconds) t2
                where t1.rid = t2.rid-1 and t1.occupancy=1 and t2.occupancy=0 and t1.id=t2.id
                group by t1.id
            ) num_rides
            where sum_table.id=num_rides.id
            order by id
        '''.format(id)
        cursor.execute(query)
        result = list(cursor.fetchone())
        result[3] = float(result[3])

        response = {
            "performance": {
                "query": query,
                "sql": get_sql_execution_time(query.replace("'", "''")),
                "python": 0
            },
            "result": result
        }
        return Response(json.dumps(response, separators=(',', ':')), mimetype='application/json')

def _convert_timestamp(ts):
    if isinstance(ts, datetime.datetime):
        return str(ts)


def _get_timestamp(fgcid, frame):
    seconds = fgcid * FRAME_GROUP_SIZE * 60 + frame * FRAME_SIZE
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(seconds))

def get_sql_execution_time(query):
    with Cursor(SCHEMA_NAME) as cursor:
        results = []

        query = '''SELECT MIN_EXECUTION_TIME 
                    FROM SYS.M_SQL_PLAN_CACHE 
                    WHERE STATEMENT_STRING LIKE '{}' 
                    ORDER BY LAST_EXECUTION_TIMESTAMP DESC
                '''.format(query)
        cursor.execute(query)
        results = cursor.fetchone()
        return float(results[0]) / 1000 # convert to ms

def calc_execution_time(start, end):
    return round((end - start) * 1000, 3)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=9001)
