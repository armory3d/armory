import socket, json, os

def connect_client(machine, port, blendpath, obj_num):

    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the remote host and port
    sock.connect((machine, port))

    #0: Blendpath, 
    #1: For all designated objects, run from 0 to number; 0 indicates all

    args = [blendpath, obj_num]

    command = json.dumps({'call':1, 'command':1, 'args':args})

    # Send a request to the host
    sock.send((command).encode())

    # Get the host's response, no more than, say, 1,024 bytes
    response_data = sock.recv(1024)

    print(response_data.decode())

    # Terminate
    sock.close()
