package armory.network;

import haxe.Constraints;

import sys.ssl.Key;
import sys.ssl.Certificate;

@:generic
class WebSocketSecureServer
	#if (haxe_ver < 4)
	<T:(Constructible<SocketImpl->Void>, Handler)>
	#else
	<T:Constructible<SocketImpl->Void> & Handler>
	#end
	extends WebSocketServer<T> {

	private var _cert:Certificate;
	private var _key:Key;
	private var _caChain:Certificate;

	public function new(host:String, port:Int, cert:Certificate, key:Key, caChain:Certificate, maxConnections:Int = 1) {
		super(host, port, maxConnections);

		_cert=cert;
		_key=key;
		_caChain=caChain;
	}


	override private function createSocket() {
		var socket = new SecureSocketImpl();
		socket.setHostname(_host);

		socket.setCA(_caChain);
		socket.setCertificate(_cert, _key);
		socket.verifyCert = false;
		return socket;
	}
}
