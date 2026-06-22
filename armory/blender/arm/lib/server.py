import atexit
import http.server
import socketserver
import subprocess

haxe_server = None


def run_tcp(port: int, do_log: bool):
    class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            if do_log:
                print(format % args)

    try:
        http_server = socketserver.TCPServer(("", port), HTTPRequestHandler)
        http_server.serve_forever()
    except:
        print("Server already running")


def run_haxe(haxe_path, port=6000):
    global haxe_server
    if haxe_server is None:
        haxe_server = subprocess.Popen([haxe_path, "--wait", str(port)])
        atexit.register(kill_haxe)


def kill_haxe():
    global haxe_server
    if haxe_server is not None:
        haxe_server.kill()
        haxe_server = None
