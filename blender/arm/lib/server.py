import http.server
import socketserver

def run():
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        httpd = socketserver.TCPServer(("", 8040), Handler)
        httpd.serve_forever()
    except:
        print('Server already running')
