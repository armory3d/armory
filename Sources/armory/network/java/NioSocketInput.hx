package armory.network.java;

import haxe.io.Bytes;
import java.io.NativeInput;
import java.io.PipedInputStream;
import java.io.PipedOutputStream;

class NioSocketInput extends NativeInput {
    public var socket:NioSocket;
    public var pipedOutputStream:PipedOutputStream;

    public function new(socket:NioSocket) {
        try {
            pipedOutputStream = new PipedOutputStream();
            super(new PipedInputStream(pipedOutputStream));
            this.socket = socket;
        } catch (e:Dynamic) {
            trace(e);
        }
    }

    public override function readBytes(s:Bytes, pos:Int, len:Int):Int {
        if (stream.available() == 0) {
            return 0;
        }
        return super.readBytes(s, pos, len);
    }
}
