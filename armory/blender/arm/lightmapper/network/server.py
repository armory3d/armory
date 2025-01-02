#!/usr/bin/env python3

import bpy, socket, json, subprocess, os, platform, subprocess, select

def startServer():

    active = True
    baking = False

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.bind(('localhost', 9898))  
    sock.listen(1)

    print("Server started")

    while active:
        connection,address = sock.accept()  

        data = connection.recv(1024)  

        if data:

            parsed_data = json.loads(data.decode())

            if parsed_data["call"] == 0: #Ping

                print("Pinged by: " + str(connection.getsockname()))
                connection.sendall(("Ping callback").encode())

            elif parsed_data["call"] == 1: #Command

                if parsed_data["command"] == 0: #Shutdown

                    print("Server shutdown")
                    active = False
                    
                if parsed_data["command"] == 1: #Baking

                    print("Baking...")

                    args = parsed_data["args"]

                    blenderpath = bpy.app.binary_path

                    if not baking:

                        baking = True

                        pipe = subprocess.Popen([blenderpath, "-b", str(args[0]), "--python-expr", 'import bpy; import thelightmapper; thelightmapper.addon.utility.build.prepare_build(0, True);'], shell=True, stdout=subprocess.PIPE)

                        stdout = pipe.communicate()[0]

                        print("Baking finished...")

                        active = False

                    else:

                        print("Request denied, server busy...")

                print("Data received: " + data.decode())

        connection.send(('Callback from: ' + str(socket.gethostname())).encode())

        connection.close()

        print("Connection closed.")

    sock.close()

    print("Server closed.")