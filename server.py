from cursor import Cursor
from flask import Flask, render_template, Response
import json

app = Flask(__name__)

SCHEMA_NAME = 'TUK3_TS_MJ'


@app.route('/')
def index():   
    return render_template('map.html')


@app.route('/timeframe/<int:fgcid>/<int:frame>')
def timeframe(fgcid, frame):
    with Cursor(SCHEMA_NAME) as cursor:
        lat = 'PF{}PX'.format(frame)
        lon = 'PF{}PY'.format(frame)
        query = '''select {0} + ify as lat, {1} + ifx as lon
                   from "TUK3_TS_MJ"."FRAMEFORMAT2"
                   where fgcid = {2}
                   and {0} is not NULL'''.format(lat, lon, fgcid)

        cursor.execute(query)
        return Response(json.dumps(cursor.fetchall()), mimetype='application/json')


@app.route('/timeframe_granularity/<int:fgcid>/<int:frame>/<int:granularity>')
def timeframe_granularity(fgcid, frame, granularity):
    # Granularity is supposed to be >= 0 and < 7
    with Cursor(SCHEMA_NAME) as cursor:
        lat = 'PF{}PX'.format(frame)
        lon = 'PF{}PY'.format(frame)
        query = '''select lat, lon, count(*) as weight from (
                            select round({0} + ify, {1}) as lat,
                                   round({2} + ifx, {1}) as lon
                            from "TUK3_TS_MJ"."FRAMEFORMAT2"
                            where fgcid = {3}
                            and {0} is not NULL)
                        group by lat, lon'''.format(lat, granularity, lon, fgcid)

        cursor.execute(query)
        return Response(json.dumps(cursor.fetchall()), mimetype='application/json')

@app.route('/route/<int:tid>')
def route_information(tid):
    with Cursor(SCHEMA_NAME) as cursor:
        query = '''select timestamp,lon,lat,occupancy
                        from shenzhen
                        where id='{}' order by timestamp
                '''.format(tid)

        cursor.execute(query)
        result = cursor.fetchall()
        
        # import pdb;pdb.set_trace()
        return Response(json.dumps([(x[0].strftime("%H:%M:%S"),x[1],x[2],x[3]) for x in result]), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True, port=9001)
