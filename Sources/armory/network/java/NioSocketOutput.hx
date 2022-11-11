package armory.network.java;

import haxe.io.BytesBuffer;
import haxe.io.BytesOutput;
import java.nio.ByteBuffer;

@:access(armory.network.java.NioSocket)
class NioSocketOutput extends BytesOutput {
    public var socket:NioSocket;

    public function new(socket:NioSocket) {
        super();
        this.socket = socket;
    }

    public override function flush() {
        var buffer = ByteBuffer.wrap(getBytes().getData());
        socket.channel.write(buffer);
        buffer.clear();
        b = new BytesBuffer();
    }
}
