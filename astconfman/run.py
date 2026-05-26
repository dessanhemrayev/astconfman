#!/usr/bin/env python   
import sys
from gevent.pywsgi import WSGIServer
from manage_commands import register_commands

from app import app
register_commands(app)

if __name__=='__main__':
    server = WSGIServer((app.config['LISTEN_ADDRESS'],
                         app.config['LISTEN_PORT']),
                        app)
    server.serve_forever()