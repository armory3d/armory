import project
import nodes_logic
import nodes_pipeline
import nodes_world
import exporter
import traits_animation
import traits_params
import traits
import props
import lib.drop_to_ground

import utils
import threading
import os
import http.server
import socketserver

def run_server():
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        httpd = socketserver.TCPServer(("", 8040), Handler)
        httpd.serve_forever()
    except:
        print('Server already running')

def register():
    props.register()
    project.register()
    nodes_logic.register()
    nodes_pipeline.register()
    nodes_world.register()
    exporter.register()
    traits_animation.register()
    traits_params.register()
    traits.register()
    lib.drop_to_ground.register()

    # Start server
    os.chdir(utils.get_fp())
    t = threading.Thread(name='localserver', target=run_server)
    t.daemon = True
    t.start()

def unregister():
    project.unregister()
    nodes_logic.unregister()
    nodes_pipeline.unregister()
    nodes_world.unregister()
    exporter.unregister()
    traits_animation.unregister()
    traits_params.unregister()
    traits.unregister()
    props.unregister()
    lib.drop_to_ground.unregister()
