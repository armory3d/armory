import http.server
import socketserver
import subprocess
import atexit

haxe_server = None

def run_tcp():
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        httpd = socketserver.TCPServer(("", 8040), Handler)
        httpd.serve_forever()
    except:
        print('Server already running')

def run_haxe(haxe_path, port=6000):
	global haxe_server
	if haxe_server == None:
		haxe_server = subprocess.Popen([haxe_path, '--wait', str(port)])
		atexit.register(kill_haxe)

def kill_haxe():
	global haxe_server
	if haxe_server != None:
		haxe_server.kill()
		haxe_server = None
