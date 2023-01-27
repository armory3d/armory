package armory.network;

class WebSocketHandler extends Handler {
	public static var MAX_WAIT_TIME:Int = 1000; // if no handshake has happened after this time (in seconds), we'll consider it dead and disconnect

	private var _creationTime:Float;

	public function new(socket:SocketImpl) {
		super(socket);
		_creationTime = Sys.time();
		_socket.setBlocking(false);
		Log.debug('New socket handler', id);
	}

	public override function handle() {
		if (this.state == State.Handshake && Sys.time() - _creationTime > (MAX_WAIT_TIME / 1000)) {
			Log.info('No handshake detected in ${MAX_WAIT_TIME}ms, closing connection', id);
			this.close();
			return;
		}
		super.handle();
	}

	private override function handleData() {
		switch (state) {
			case State.Handshake:
				var httpRequest = recvHttpRequest();
				if (httpRequest == null) {
					return;
				}

				handshake(httpRequest);
				handleData();
			case _:
				super.handleData();
		}
	}

	public function handshake(httpRequest:HttpRequest) {
		var httpResponse = new HttpResponse();

		httpResponse.headers.set(HttpHeader.SEC_WEBSOSCKET_VERSION, "13");
		if (httpRequest.method != "GET" || httpRequest.httpVersion != "HTTP/1.1") {
			httpResponse.code = 400;
			httpResponse.text = "Bad";
			httpResponse.headers.set(HttpHeader.CONNECTION, "close");
			httpResponse.headers.set(HttpHeader.X_WEBSOCKET_REJECT_REASON, 'Bad request');
		} else if (httpRequest.headers.get(HttpHeader.SEC_WEBSOSCKET_VERSION) != "13") {
			httpResponse.code = 426;
			httpResponse.text = "Upgrade";
			httpResponse.headers.set(HttpHeader.CONNECTION, "close");
			httpResponse.headers.set(HttpHeader.X_WEBSOCKET_REJECT_REASON, 'Unsupported websocket client version: ${httpRequest.headers.get(HttpHeader.SEC_WEBSOSCKET_VERSION)}, Only version 13 is supported.');
		} else if (httpRequest.headers.get(HttpHeader.UPGRADE) != "websocket") {
			httpResponse.code = 426;
			httpResponse.text = "Upgrade";
			httpResponse.headers.set(HttpHeader.CONNECTION, "close");
			httpResponse.headers.set(HttpHeader.X_WEBSOCKET_REJECT_REASON, 'Unsupported upgrade header: ${httpRequest.headers.get(HttpHeader.UPGRADE)}.');
		} else if (httpRequest.headers.get(HttpHeader.CONNECTION).indexOf("Upgrade") == -1) {
			httpResponse.code = 426;
			httpResponse.text = "Upgrade";
			httpResponse.headers.set(HttpHeader.CONNECTION, "close");
			httpResponse.headers.set(HttpHeader.X_WEBSOCKET_REJECT_REASON, 'Unsupported connection header: ${httpRequest.headers.get(HttpHeader.CONNECTION)}.');
		} else {
			Log.debug('Handshaking', id);
			var key = httpRequest.headers.get(HttpHeader.SEC_WEBSOCKET_KEY);
			var result = makeWSKeyResponse(key);
			Log.debug('Handshaking key - ${result}', id);

			httpResponse.code = 101;
			httpResponse.text = "Switching Protocols";
			httpResponse.headers.set(HttpHeader.UPGRADE, "websocket");
			httpResponse.headers.set(HttpHeader.CONNECTION, "Upgrade");
			httpResponse.headers.set(HttpHeader.SEC_WEBSOSCKET_ACCEPT, result);
		}

		sendHttpResponse(httpResponse);

		if (httpResponse.code == 101) {
			_onopenCalled = false;
			state = State.Head;
			Log.debug('Connected', id);
		} else {
			close();
		}
	}
}
