package armory.network;

import armory.network.Types;

#if js

import haxe.Constraints.Function;
import haxe.io.Bytes;

#if (haxe_ver < 4)
	typedef JsBuffer = js.html.ArrayBuffer;
#else
	typedef JsBuffer = js.lib.ArrayBuffer;
#end

class WebSocket {
	private var _url:String;

	private var _ws:js.html.WebSocket = null;

	public function new(url:String, immediateOpen=true) {
		_url = url;
		if (immediateOpen) {
			open();
		}
	}

	private function createSocket() {
		return new js.html.WebSocket(_url);
	}

	public function open() {
		if (_ws != null) {
			throw "Socket already connected";
		}
		_ws = createSocket();
		set_binaryType(Types.BinaryType.ARRAYBUFFER);
		if (_onopenbeforeready != null) {
			onopen = _onopenbeforeready;
			_onopenbeforeready = null;
		}
		if (_onclosebeforeready != null) {
			onclose = _onclosebeforeready;
			_onclosebeforeready = null;
		}
		if (_onerrorbeforeready != null) {
			onerror = _onerrorbeforeready;
			_onerrorbeforeready = null;
		}
		if (_onmessagebeforeready != null) {
			onmessage = _onmessagebeforeready;
			_onmessagebeforeready = null;
		}
	}

	private var _onopenbeforeready:Function = null;
	public var onopen(get, set):Function;
	private function get_onopen():Function {
		return _ws.onopen;
	}
	private function set_onopen(value:Function):Function {
		if (_ws == null) {
			_onopenbeforeready = value;
			return value;
		}
		_ws.onopen = value;
		return value;
	}

	private var _onclosebeforeready:Function = null;
	public var onclose(get, set):Function;
	private function get_onclose():Function {
		return _ws.onclose;
	}
	private function set_onclose(value:Function):Function {
		if (_ws == null) {
			_onclosebeforeready = value;
			return value;
		}
		_ws.onclose = value;
		return value;
	}

	private var _onerrorbeforeready:Function = null;
	public var onerror(get, set):Function;
	private function get_onerror():Function {
		return _ws.onerror;
	}
	private function set_onerror(value:Function):Function {
		if (_ws == null) {
			_onerrorbeforeready = value;
			return value;
		}
		_ws.onerror = value;
		return value;
	}

	private var _onmessagebeforeready:Function = null;
	private var _onmessage:Function = null;
	public var onmessage(get, set):Function;
	private function get_onmessage():Function {
		return _onmessage;
	}
	private function set_onmessage(value:Function):Function {
		if (_ws == null) {
			_onmessagebeforeready = value;
			return value;
		}
		_onmessage = value;
		_ws.onmessage = function(message: Dynamic) {
			if (_onmessage != null) {
				if (Std.isOfType(message.data, JsBuffer)) {
					var buffer = new Buffer();
					buffer.writeBytes(Bytes.ofData(message.data));
					_onmessage(BytesMessage(buffer));
				} else {
					_onmessage(StrMessage(message.data));
				}
			}
		};
		return value;
	}

	public var binaryType(get, set):BinaryType;
	private function get_binaryType() {
		return _ws.binaryType;
	}
	private function set_binaryType(value:BinaryType):BinaryType {
		_ws.binaryType = value;
		return value;
	}

	public function close() {
		_ws.close();
		onopen = null;
		onclose = null;
		onerror = null;
		onmessage = null;
		_onmessage = null;
		_ws = null;
	}

	public function send(msg:Any) {
		if (Std.isOfType(msg, Bytes)) {
			var bytes = cast(msg, Bytes);
			_ws.send(bytes.getData());
		} else if (Std.isOfType(msg, Buffer)) {
			var buffer = cast(msg, Buffer);
			_ws.send(buffer.readAllAvailableBytes().getData());
		} else {
			_ws.send(msg);
		}
	}
}

#elseif sys

#if (haxe_ver >= 4)
import sys.thread.Thread;
#elseif neko
import neko.vm.Thread;
#elseif cpp
import cpp.vm.Thread;
#end

import haxe.crypto.Base64;
import haxe.io.Bytes;

class WebSocket extends WebSocketCommon {
	public var _protocol:String;
	public var _host:String;
	public var _port:Int = 0;
	public var _path:String;

	private var _processThread:Thread;
	private var _encodedKey:String = "wskey";

	public var binaryType:BinaryType;

	public var additionalHeaders(get, null):Map<String, String>;

	public function new(url:String, immediateOpen=true) {
		parseUrl(url);

		super(createSocket());

		if (immediateOpen) {
			open();
		}
	}

	inline private function parseUrl(url)
	{	
		/** TO DO - FIND OUT WHAT IS BREAKING REGEX IN THE NEW PCRE2 FOR HL C 

		var urlRegExp = ~/^(\w+?):\/\/([\w\.-]+)(:(\d+))?(\/.*)?$/;

		if ( ! urlRegExp.match(url)) {
			throw 'Uri not matching websocket URL "${url}"';
		}

		_protocol = urlRegExp.matched(1);

		_host = urlRegExp.matched(2);

		var parsedPort = Std.parseInt(urlRegExp.matched(4));
		if (parsedPort > 0 ) {
			_port = parsedPort;
		}
		_path = urlRegExp.matched(5);
		if (_path == null || _path.length == 0) {
			_path = "/";
		}
		**/
		var urlArr = url.split(":");
		if ( urlArr.length < 3) {
			throw 'Uri not matching websocket URL "${url}"';
		}
		_protocol = urlArr[0];
		_host = urlArr[1].substr(2, urlArr[1].length);
		var parsedPort = Std.parseInt(urlArr[2].split("/")[0]);
		if (parsedPort > 0 ) {
			_port = parsedPort;
		}
		_path = urlArr[2].substr(urlArr[2].split("/")[0].length, urlArr[2].length);
		if (_path == null || _path.length == 0) {
			_path = "/";
		}
	}


	private function createSocket():SocketImpl
	{
		if (_protocol == "wss") {
			#if (java || cs)
				throw "Secure sockets not implemented";
			#else
				if (_port == 0) {
					_port = 443;
				}
				return new SecureSocketImpl();
			#end
		} else if (_protocol == "ws") {
			if (_port == 0) {
				_port = 80;
			}
			return new SocketImpl();
		} else {
			throw 'Unknown protocol $_protocol';
		}
	}


	public function open() {
		if (state != State.Handshake) {
			throw "Socket already connected";
		}
		_socket.setBlocking(true);
		_socket.connect(new sys.net.Host(_host), _port);
		_socket.setBlocking(false);

		#if !cs

		_processThread = Thread.create(processThread);
		_processThread.sendMessage(this);

		#else

		haxe.MainLoop.addThread(function() {
			Log.debug("Thread started", this.id);
			processLoop(this);
			Log.debug("Thread ended", this.id);
		});

		#end

		sendHandshake();
	}

	private function processThread() {
		Log.debug("Thread started", this.id);
		var ws:WebSocket = Thread.readMessage(true);
		processLoop(this);
		Log.debug("Thread ended", this.id);
	}

	private function processLoop(ws:WebSocket) {
		while (ws.state != State.Closed) { // TODO: should think about mutex
			ws.process();
			Sys.sleep(.01);
		}
	}

	function get_additionalHeaders() {
		if (additionalHeaders == null) {
			additionalHeaders = new Map<String, String>();
		}
		return additionalHeaders;
	}

	public function sendHandshake() {
		var httpRequest = new HttpRequest();
		httpRequest.method = "GET";
		// TODO: should propably be hostname+port+path?
		httpRequest.uri = _path;
		httpRequest.httpVersion = "HTTP/1.1";

		httpRequest.headers.set(HttpHeader.HOST, _host + ":" + _port);
		httpRequest.headers.set(HttpHeader.USER_AGENT, "hxWebSockets");
		httpRequest.headers.set(HttpHeader.SEC_WEBSOSCKET_VERSION, "13");
		httpRequest.headers.set(HttpHeader.UPGRADE, "websocket");
		httpRequest.headers.set(HttpHeader.CONNECTION, "Upgrade");
		httpRequest.headers.set(HttpHeader.PRAGMA, "no-cache");
		httpRequest.headers.set(HttpHeader.CACHE_CONTROL, "no-cache");
		httpRequest.headers.set(HttpHeader.ORIGIN, _socket.host().host.toString() + ":" + _socket.host().port);


		_encodedKey = generateWSKey();
		httpRequest.headers.set(HttpHeader.SEC_WEBSOCKET_KEY, _encodedKey);

		if (additionalHeaders != null) {
			for ( k in additionalHeaders.keys()) {
				httpRequest.headers.set(k, additionalHeaders[k]);
			}
		}

		sendHttpRequest(httpRequest);
	}

	private override function handleData() {
		switch (state) {
			case State.Handshake:
				var httpResponse = recvHttpResponse();
				if (httpResponse == null) {
					return;
				}

				handshake(httpResponse);
				handleData();
			case _:
				super.handleData();
		}

	}

	private function handshake(httpResponse:HttpResponse) {
		if (httpResponse.code != 101) {
			if (onerror != null) {
				onerror(httpResponse.headers.get(HttpHeader.X_WEBSOCKET_REJECT_REASON));
			}
			close();
			return;
		}

		var secKey = httpResponse.headers.get(HttpHeader.SEC_WEBSOSCKET_ACCEPT);

		if (secKey == null) {
			trace("This server does not use Sec-WebSocket-Key WebSocket handshake.");
		} else {
			if (secKey != makeWSKeyResponse(_encodedKey)) {
				if (onerror != null) {
					onerror("Error during WebSocket handshake: Incorrect 'Sec-WebSocket-Accept' header value");
				}
				close();
				return;
			}
		}

		_onopenCalled = false;
		state = State.Head;
	}

	private function generateWSKey():String {
		var b = Bytes.alloc(16);
		for (i in 0...16) {
			b.set(i, Std.random(255));
		}
		return Base64.encode(b);
	}
}

#end
