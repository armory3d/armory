package armory.network.nodejs;

import haxe.io.Bytes;
import js.node.Buffer;

@:access(armory.network.nodejs.NodeSocket)
class NodeSocketInput {
    private var _socket:NodeSocket;

    public var hasData = false;

    private var _buffer: Buffer = null;
    public function new(socket:NodeSocket) {
        _socket = socket;
        _socket._socket.on("data", onData);
    }

    private function onData(data:Any) {
        var a = [];
        if (_buffer != null) {
            a.push(_buffer);
        }
        a.push(Buffer.from(data));
        _buffer = Buffer.concat(a);
        hasData = true;
    }

    public function readBytes(s:Bytes, pos:Int, len:Int):Int {
        if (_buffer == null) {
            return 0;
        }
        var n:Int = _buffer.length;
        if (n > len) {
            n = len;
        }
        if (len > n) {
            len = n;
        }
        var part = _buffer.slice(0, len);
        var remain = null;
        if (_buffer.length > len) {
            remain = _buffer.slice(len);
        }
        var src = part.hxToBytes();
        s.blit(pos, src, 0, len);
        hasData = (remain != null);
        _buffer = remain;
        return n;
    }
}
