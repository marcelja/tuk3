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
        cursor.execute('call locations_at_timeframe({}, {}, ?)'
                       .format(fgcid, frame))
        # TODO: adapt return type
        return Response(json.dumps(cursor.fetchall()), mimetype='application/json')


@app.route('/timeframe_granularity/<int:fgcid>/<int:frame>/<int:granularity>')
def timeframe_granularity(fgcid, frame, granularity):
    # Granularity is supposed to be >= 0 and < 7
    with Cursor(SCHEMA_NAME) as cursor:
        cursor.execute('call locations_at_timeframe_granularity({}, {}, {}, ?)'
                       .format(fgcid, frame, granularity))
        # TODO: adapt return type
        #return str(cursor.fetchall())
        return Response(json.dumps(cursor.fetchall()), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True, port=9001)
