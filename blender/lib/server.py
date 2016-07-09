import http.server
import socketserver
import bpy
import os

# Can't use multiprocessing on Windows
#p = Process(target=run_server)
#p.start()
#atexit.register(p.terminate)

def run_server():
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", 8040), Handler)
    httpd.serve_forever()

run_server()
