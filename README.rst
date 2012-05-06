tracebin
========

Tracebin is a small flask application to receive Python tracebacks formatted with `offlinetb <https://github.com/vmalloc/offlinetb>`_. Simply POST the resulting JSON to the root url, and the app sends back the resulting uuid::

  POST / HTTP/1.0
  ...

  <<traceback data here>>

Returns::

  HTTP/1.0 200 OK
  Content-type: application/json
  Content-Length: 107
  ...

  {
      "id": "d9c7d8c5974911e189b7c82a1414d2bb",
      "url": "http://yoursever.com/d9c7d8c5974911e189b7c82a1414d2bb"
  }

Subsequently, when you try to browse the resulting URL with a web browser, you'll be able to interactively explore the traceback and its frames.

This is particularly useful when deploying in-house solutions which occasionally fail and would like to report the failure details to a centralized location. This small utility enables you to just save the traceback URL and link to it from anywhere you want.

Installation
============

1. Clone the repository to anywhere you want (say /opt/tracebin/ on your server)
2. (optional) Create a Python virtualenv to run your application:
   virtualenv /opt/tracebin/env
3. Install requirements::

   /opt/tracebin/env/bin/pip install -r /opt/tracebin/env/src/pip_requirements.txt
4. To run the server as scgi, just run::

   /opt/tracebin/env/bin/python /opt/tracebin/src/app.py scgi -d /your/data/dir -s /path/to/socket/file
5. If you'd like your app to be installed on some URL path other than '/', use the '-r' flag to specify a url prefix
