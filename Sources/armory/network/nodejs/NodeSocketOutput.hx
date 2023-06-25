package armory.network.nodejs;

import haxe.io.Bytes;
import js.node.Buffer;

@:access(armory.network.nodejs.NodeSocket)
class NodeSocketOutput {
    private var _socket:NodeSocket;
    
    private var _buffer:Buffer = null;
    public function new(socket:NodeSocket) {
        _socket = socket;
    }
    
    public function write(data:Bytes) {
        var a = [];
        if (_buffer != null) {
            a.push(_buffer);
        }
        a.push(Buffer.hxFromBytes(data));
        _buffer = Buffer.concat(a);
    }
    
    public function flush() {
        _socket._socket.write(_buffer);
        _buffer = null;
    }
}
