package armory.network.java;

import java.NativeArray;
import java.lang.System;
import java.net.InetSocketAddress;
import java.net.SocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.types.Int8;
import sys.net.Host;

@:access(sys.net.Host)
class NioSocket {

    public var input(default,null) : haxe.io.Input;
    public var output(default,null) : haxe.io.Output;

    public var custom : Dynamic;

    private var sock:java.net.Socket;
    private var server:java.net.ServerSocket;

    private var selector:Selector;
    private var serverChannel:ServerSocketChannel;
    private var channel:SocketChannel;

    private var boundAddr:SocketAddress;

    public function new():Void {
    }

    private function createServer():Void {
        if (selector == null && serverChannel == null) {
            this.selector = Selector.open();
            this.serverChannel = ServerSocketChannel.open();
            serverChannel.configureBlocking(false);
        }
    }

    public function close():Void {
        if (serverChannel != null) {
            server.close();
        }
        if (channel != null) {
            channel.close();
        }
    }

    public function read():String {
        return input.readAll().toString();
    }

    public function write(content:String):Void {
        output.writeString(content);
    }

    public function connect(host:Host, port:Int):Void {
        sock.connect(new InetSocketAddress(host.wrapped, port));
        /*
        this.output = new java.io.NativeOutput(sock.getOutputStream());
        this.input = new java.io.NativeInput(sock.getInputStream());
        */
    }

    public function listen(connections:Int):Void {
        if (boundAddr == null) {
            throw "You must bind the Socket to an address!";
        }

        createServer();
        serverChannel.bind(boundAddr, connections);
        serverChannel.register(selector, SelectionKey.OP_ACCEPT);
    }

    public function shutdown(read:Bool, write:Bool):Void {
        throw "Not implemented";
    }

    public function bind( host:Host, port:Int):Void {
        if (boundAddr != null) {
            if (server.isBound()) throw "Already bound";
        }
        createServer();
        this.boundAddr = new InetSocketAddress(host.wrapped, port);
    }

    public function accept():NioSocket {
        if (selector.select() <= 0) {
            throw "Blocking"; // not really the right thing to throw
        }

        var selectedKeys = selector.selectedKeys();
        var iterator = selectedKeys.iterator();
        if (iterator.hasNext() == false) {
            throw "Blocking"; // not really the right thing to throw
        }
        var key = cast(iterator.next(), SelectionKey);
        iterator.remove();
        if (key.isAcceptable() == false) {
            throw "Blocking"; // not really the right thing to throw
        }

        var sc = serverChannel.accept();
        sc.configureBlocking(false);
        sc.register(selector, SelectionKey.OP_READ | SelectionKey.OP_WRITE);
        var s = new NioSocket();
        s.channel = sc;
        s.selector = selector;

        s.output = new NioSocketOutput(s);
        s.input = new NioSocketInput(s);

        return s;
    }

    public function peer():{host:Host, port:Int} {
        throw "Not implemented";
        return null;
    }

    public function host():{host:Host, port:Int} {
        throw "Not implemented";
        return null;
    }

    public function setTimeout(timeout:Float ):Void {
        throw "Not implemented";
    }

    public function waitForRead():Void {
        throw "Not implemented";
    }

    public function setBlocking(b:Bool):Void {
    }

    public function setFastSend(b:Bool):Void {
        throw "Not implemented";
    }

    public static function select(read:Array<NioSocket>, write:Array<NioSocket>, others:Array<NioSocket>, ?timeout:Float) : { read:Array<NioSocket>, write:Array<NioSocket>, others:Array<NioSocket> } {
        if (write != null && write.length > 0) {
            throw "Not implemented";
        }
        if (others != null && others.length > 0) {
            throw "Not implemented";
        }

        var ret = null;
        if (read != null && read.length > 0) {
            for (r in read) {
                if (r.selector.select() > 0) {
                    var selectedKeys = r.selector.selectedKeys();
                    var iterator = selectedKeys.iterator();
                    while (iterator.hasNext()) {
                        var key = cast(iterator.next(), SelectionKey);
                        iterator.remove();
                        if (key.isReadable()) {
                            if (ret == null) {
                                ret = {
                                    read: [],
                                    write: null,
                                    others: null
                                }
                            }
                            ret.read.push(r);
                            var buffer = ByteBuffer.allocate(1024);
                            var bytesRead = r.channel.read(buffer);
                            if (bytesRead == -1) {
                                r.channel.close();
                                key.cancel();
                                throw "Blocking"; // not really the right thing to throw
                            }
                            var copy:NativeArray<Int8> = new NativeArray(bytesRead);
                            System.arraycopy(buffer.array(), 0, copy, 0, bytesRead);
                            cast(r.input, NioSocketInput).pipedOutputStream.write(copy, 0, bytesRead);
                        }
                    }
                }
            }
        }

        return ret;
    }
}
