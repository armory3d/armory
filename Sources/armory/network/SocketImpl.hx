package armory.network;

#if java

typedef SocketImpl = armory.network.java.NioSocket;

#elseif cs

typedef SocketImpl = armory.network.cs.NonBlockingSocket;

#elseif nodejs

typedef SocketImpl = armory.network.nodejs.NodeSocket;

#else

typedef SocketImpl = sys.net.Socket;

#end
