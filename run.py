#!/usr/bin/env python3

from gevent.pywsgi import WSGIServer
from smartkar import app

server = WSGIServer(("127.0.0.1", 7777), app)
server.serve_forever()
