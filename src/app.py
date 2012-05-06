import argparse
import logging
import os
import sys
import uuid
from urlparse import urljoin

from flask import (
    Flask,
    abort,
    make_response,
    render_template,
    request,
    )
import cjson

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == 'POST':
        return _upload_traceback()
    return _render_template('index.html', url=request.url)

@app.route("/<traceback_id>")
def get_traceback_page(traceback_id):
    return _render_template('render_traceback.html', traceback_id=traceback_id)

@app.route("/_t/<traceback_id>")
def get_traceback_json(traceback_id):
    traceback_filename = os.path.join(app.config['DATA_DIR'], traceback_id)
    if not os.path.isfile(traceback_filename):
        abort(404)
    with open(traceback_filename) as f:
        return _as_json(f.read())

def _as_json(data):
    response = make_response(data)
    response.headers["Content-type"] = "application/json"
    return response

def _render_template(*args, **kwargs):
    return render_template(APPLICATION_ROOT=app.config['APPLICATION_ROOT'], *args, **kwargs)

def _upload_traceback():
    traceback_id = _get_traceback_id()
    with open(os.path.join(app.config['DATA_DIR'], traceback_id), "w") as f:
        f.write(request.input_stream.read(request.headers.get('content-length', type=int) or 0))
    response = make_response()
    return _as_json(cjson.encode({"id" : traceback_id, "url" : _get_url(traceback_id)}))

def _get_url(traceback_id):
    returned_url = request.url
    if not returned_url.endswith("/"):
        returned_url += "/"
    returned_url += traceback_id
    return returned_url

def _get_traceback_id():
    data_dir = app.config['DATA_DIR']
    while True:
        returned = str(uuid.uuid1()).replace("-", "")
        if not os.path.exists(os.path.join(data_dir, returned)):
            return returned
        # else we try again with a new uuid (highly unlikely but we still must be prepared :-)

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data-dir", default="/tmp")
parser.add_argument("-r", "--app-root", default="")
subparsers = parser.add_subparsers()

def _run_debug_server(args):
    logging.basicConfig(level='DEBUG', stream=sys.stderr)
    app.run(debug=True)

main_parser = subparsers.add_parser("debug", help="Run debug server")
main_parser.set_defaults(func=_run_debug_server)

def _run_scgi(args):
    from flup.server.scgi import WSGIServer
    WSGIServer(app, bindAddress=args.socket).run()

scgi_parser = subparsers.add_parser("scgi", help="Run scgi server")
scgi_parser.add_argument("-s", "--socket")
scgi_parser.set_defaults(func=_run_scgi)

if __name__ == "__main__":
    args = parser.parse_args()
    app.config['DATA_DIR'] = args.data_dir
    app.config['APPLICATION_ROOT'] = args.app_root
    sys.exit(args.func(args))
