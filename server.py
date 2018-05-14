from cursor import Cursor
from flask import Flask


app = Flask(__name__)

SCHEMA_NAME = 'TUK3_TS_MJ'
THREADS = 8


@app.route('/timeframe/<int:fgcid>/<int:frame>')
def timeframe(fgcid, frame):
    with Cursor(SCHEMA_NAME) as cursor:
        cursor.execute('call locations_at_timeframe({}, {}, ?)'.format(fgcid, frame))
        # TODO: adapt return type
        return str(cursor.fetchall())


if __name__ == '__main__':
    app.run(debug=True, port=9001)
