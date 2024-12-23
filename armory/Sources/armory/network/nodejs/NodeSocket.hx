package armory.network.nodejs;

import js.node.Net;
import js.node.net.Server;
import js.node.net.Socket;
import sys.net.Host;

class NodeSocket {
    public function new() {
    }

    private var _socket:Socket = null;
    public var input:NodeSocketInput = null;
    public var output:NodeSocketOutput = null;
    private function setSocket(s:Socket) {
        _socket = s;
        input = new NodeSocketInput(this);
        output = new NodeSocketOutput(this);
    }

    private var _server:Server = null;
    private function createServer():Void {
        if (_server == null) {
            _server = Net.createServer(acceptConnection);
        }
    }

    private static var _connections:Array<NodeSocket> = [];
    private var _newConnections:Array<NodeSocket> = [];
    private function acceptConnection(socket:Socket) {
        socket.setTimeout(0);
        var nodeSocket = new NodeSocket();
        nodeSocket.setSocket(socket);
        _connections.push(nodeSocket);
        _newConnections.push(nodeSocket);
    }

    public function accept() {
        if (_newConnections.length == 0) {
            throw "Blocking";
        }

        var socket = _newConnections.pop();
        return socket;

    }

    public function listen(connections:Int):Void {
        if (_host == null) {
            throw "You must bind the Socket to an address!";
        }

        createServer();
        _server.listen({
            host: _host.host,
            port: _port,
            backlog: connections
        });
    }

    private var _host:Host = null;
    private var _port:Int;
    public function bind(host:Host, port:Int):Void {
        _host = host;
        _port = port;
    }

    public function setBlocking(blocking:Bool) {

    }

    public function setTimeout(timeout:Int) {
    }

    public function close() {
        if (_server != null) {
            _server.close();
        }
        if (_socket != null) {
            _socket.destroy();
        }
    }

    public static function select(read : Array<SocketImpl>, write : Array<SocketImpl>, others : Array<SocketImpl>, ?timeout : Float) : { read: Array<SocketImpl>, write: Array<SocketImpl>, others: Array<SocketImpl> } {
        if (write != null && write.length > 0) {
            throw "Not implemented";
        }
        if (others != null && others.length > 0) {
            throw "Not implemented";
        }

        var ret = null;
        for (c in _connections) {
            if (read.indexOf(c) != -1) {
                if (c.input.hasData == true) {
                    if (ret == null) {
                        ret = {
                            read: [],
                            write: null,
                            others: null
                        }
                    }
                    ret.read.push(c);
                }
            }
        }

        return ret;
    }
}
