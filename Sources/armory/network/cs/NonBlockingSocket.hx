package armory.network.cs;

import sys.net.Socket;
import cs.system.net.sockets.Socket in NativeSocket;
import cs.system.net.sockets.NetworkStream;
import cs.system.net.sockets.SocketAsyncEventArgs;
 
class NonBlockingSocket extends Socket {
    private var _acceptedSockets:Array<NativeSocket> = [];
    private var _socketAsyncEventArgs:SocketAsyncEventArgs = null;

    public function new() {
        super();
        setBlocking(false);

    }

    public override function accept():NonBlockingSocket {
        if (_acceptedSockets.length > 0) {
            var n = _acceptedSockets.shift();
            var r = new NonBlockingSocket();
            r.sock = n;
            r.output = new cs.io.NativeOutput( new NetworkStream(r.sock) );
            r.input = new cs.io.NativeInput( new NetworkStream(r.sock) );
            return r;
        }

        if (_socketAsyncEventArgs == null) {
            _socketAsyncEventArgs = new SocketAsyncEventArgs();
            _socketAsyncEventArgs.add_Completed(onAcceptCompleted);
            sock.AcceptAsync(_socketAsyncEventArgs);
        }
        throw "Blocking";
    }

    private function onAcceptCompleted(sender:Dynamic, e:SocketAsyncEventArgs) {
        _acceptedSockets.push(e.AcceptSocket);
        _socketAsyncEventArgs = null;
    }

    public static function select(read : Array<Socket>, write : Array<Socket>, others : Array<Socket>, ?timeout : Float) : { read: Array<Socket>, write: Array<Socket>, others: Array<Socket> } {
        return Socket.select(read, write, others, timeout);
    }
}
