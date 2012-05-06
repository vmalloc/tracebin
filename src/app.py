import argparse
import logging
import os
import sys
import uuid

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
    return "Upload your traceback here"

@app.route("/t/<traceback_id>")
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
    traceback_id = str(uuid.uuid1()).replace("-", "")
    with open(os.path.join(app.config['DATA_DIR'], traceback_id), "w") as f:
        f.write(request.data)
    response = make_response(cjson.encode({"id" : traceback_id}))
    response.headers["Content-type"] = "application/json"
    return response

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data-dir", default="/tmp")
parser.add_argument("-r", "--app-root", default="")
subparsers = parser.add_subparsers()

def _run_debug_server(args):
    logging.basicConfig(level='DEBUG', stream=sys.stderr)
    app.run(debug=True)

main_parser = subparsers.add_parser("debug", help="Run debug server")
main_parser.set_defaults(func=_run_debug_server)

def _run_fcgi(args):
    from flup.server.fcgi import WSGIServer
    WSGIServer(app).run()

fcgi_parser = subparsers.add_parser("fcgi", help="Run fcgi server")
fcgi_parser.set_defaults(func=_run_fcgi)

if __name__ == "__main__":
    args = parser.parse_args()
    app.config['DATA_DIR'] = args.data_dir
    app.config['APPLICATION_ROOT'] = args.app_root
    sys.exit(args.func(args))
