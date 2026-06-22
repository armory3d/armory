package armory.network;

import armory.network.Types.MessageType;
import haxe.crypto.Base64;
import haxe.crypto.Sha1;
import haxe.io.Bytes;
import haxe.io.Error;
import armory.network.Util;

class WebSocketCommon {
	public var id:String;
	public var state:State = State.Handshake;

	public var isClient = true;

	private var _socket:SocketImpl;

	private var _onopenCalled:Null<Bool> = null;
	private var _lastError:Dynamic = null;

	public var onopen:Void->Void;
	public var onclose:Void->Void;
	public var onerror:Dynamic->Void;
	public var onmessage:MessageType->Void;

	private var _buffer:Buffer = new Buffer();

	public function new(socket:SocketImpl = null) {
		id = Util.generateUUID();
		if (socket == null) {
			_socket = new SocketImpl();
		} else {
			_socket = socket;
		}
		_socket.setBlocking(false);
		_socket.setTimeout(0);
	}

	public function send(data:Any) {
		if (Std.isOfType(data, String)) {
			Log.data(data, id);
			sendFrame(Utf8Encoder.encode(data), OpCode.Text);
		} else if (Std.isOfType(data, Bytes)) {
			sendFrame(data, OpCode.Binary);
		} else if (Std.isOfType(data, Buffer)) {
			sendFrame(cast(data, Buffer).readAllAvailableBytes(), OpCode.Binary);
		}
	}

	private function sendFrame(data:Bytes, type:OpCode) {
		writeBytes(prepareFrame(data, type, true));
	}

	private var _isFinal:Bool;
	private var _isMasked:Bool;
	private var _opcode:OpCode;
	private var _frameIsBinary:Bool;
	private var _partialLength:Int;
	private var _length:Int;
	private var _mask:Bytes;
	private var _payload:Buffer = null;
	private var _lastPong:Date = null;

	private function handleData() {
		switch (state) {
			case State.Head:
				if (_buffer.available < 2) return;

				var b0 = _buffer.readByte();
				var b1 = _buffer.readByte();

				_isFinal = ((b0 >> 7) & 1) != 0;
				_opcode = cast(((b0 >> 0) & 0xF), OpCode);
				_frameIsBinary = if (_opcode == OpCode.Text) false; else if (_opcode == OpCode.Binary) true; else _frameIsBinary;
				_partialLength = ((b1 >> 0) & 0x7F);
				_isMasked = ((b1 >> 7) & 1) != 0;

				state = State.HeadExtraLength;
				handleData(); // may be more data
			case State.HeadExtraLength:
				if (_partialLength == 126) {
					if (_buffer.available < 2) return;
					_length = _buffer.readUnsignedShort();
				} else if (_partialLength == 127) {
					if (_buffer.available < 8) return;
					var tmp = _buffer.readUnsignedInt();
					if(tmp != 0) throw 'message too long';
					_length = _buffer.readUnsignedInt();
				} else {
					_length = _partialLength;
				}
				state = State.HeadExtraMask;
				handleData(); // may be more data
			case State.HeadExtraMask:
				if (_isMasked) {
					if (_buffer.available < 4) return;
					_mask = _buffer.readBytes(4);
				}
				state = State.Body;
				handleData(); // may be more data
			case State.Body:
				if (_buffer.available < _length) return;
				if (_payload == null) {
					_payload = new Buffer();
				}
				_payload.writeBytes(_buffer.readBytes(_length));

				switch (_opcode) {
					case OpCode.Binary | OpCode.Text | OpCode.Continuation:
						if (_isFinal) {
							var messageData = _payload.readAllAvailableBytes();
							var unmaskedMessageData = (_isMasked) ? applyMask(messageData, _mask) : messageData;
							if (_frameIsBinary) {
								if (this.onmessage != null) {
									var buffer = new Buffer();
									buffer.writeBytes(unmaskedMessageData);
									this.onmessage(BytesMessage(buffer));
								}
							} else {
								var stringPayload = Utf8Encoder.decode(unmaskedMessageData);
								Log.data(stringPayload, id);
								if (this.onmessage != null) {
									this.onmessage(StrMessage(stringPayload));
								}
							}
							_payload = null;
						}
					case OpCode.Ping:
						sendFrame(_payload.readAllAvailableBytes(), OpCode.Pong);
					case OpCode.Pong:
						_lastPong = Date.now();
					case OpCode.Close:
						close();
				}

				if (state != State.Closed) state = State.Head;
				handleData(); // may be more data
			case State.Closed:
				close();
			case _:
				trace('State not impl: ${state}');
		}
	}

	public function close() {
		if (state != State.Closed) {
			try {
				Log.debug("Closed", id);
				sendFrame(Bytes.alloc(0), OpCode.Close);
				state = State.Closed;
				_socket.close();
			} catch (e:Dynamic) { }

			if (onclose != null) {
				onclose();
			}
		}
	}

	private function writeBytes(data:Bytes) {
		try {
			_socket.output.write(data);
			_socket.output.flush();
		} catch (e:Dynamic) {
			Log.debug(Std.string(e), id);
			if (onerror != null) {
				onerror(Std.string(e));
			}
		}
	}

	private function prepareFrame(data:Bytes, type:OpCode, isFinal:Bool):Bytes {
		var out = new Buffer();
		var isMasked = isClient; // All clientes messages must be masked: http://tools.ietf.org/html/rfc6455#section-5.1
		var mask = generateMask();
		var sizeMask = (isMasked ? 0x80 : 0x00);

		out.writeByte(type.toInt() | (isFinal ? 0x80 : 0x00));

		if (data.length < 126) {
			out.writeByte(data.length | sizeMask);
		} else if (data.length < 65536) {
			out.writeByte(126 | sizeMask);
			out.writeShort(data.length);
		} else {
			out.writeByte(127 | sizeMask);
			out.writeInt(0);
			out.writeInt(data.length);
		}

		if (isMasked) out.writeBytes(mask);

		out.writeBytes(isMasked ? applyMask(data, mask) : data);
		return out.readAllAvailableBytes();
	}

	private static function generateMask() {
		var maskData = Bytes.alloc(4);
		maskData.set(0, Std.random(256));
		maskData.set(1, Std.random(256));
		maskData.set(2, Std.random(256));
		maskData.set(3, Std.random(256));
		return maskData;
	}

	private static function applyMask(payload:Bytes, mask:Bytes) {
		var maskedPayload = Bytes.alloc(payload.length);
		for (n in 0 ... payload.length) maskedPayload.set(n, payload.get(n) ^ mask.get(n % mask.length));
		return maskedPayload;
	}

	private function process() {
		if (_onopenCalled == false) {
			_onopenCalled = true;
			if (onopen != null) {
				onopen();
			}
		}

		if (_lastError != null) {
			var error = _lastError;
			_lastError = null;
			if (onerror != null) {
				onerror(error);
			}
		}

		var needClose = false;
		var result = null;
		try {
			result = SocketImpl.select([_socket], null, null, 0.01);
		} catch (e:Dynamic) {
			Log.debug("Error selecting socket: " + e);
			needClose = true;
		}

		if (result != null && needClose == false) {
			if (result.read.length > 0) {
				try {
					while (true) {
						var data = Bytes.alloc(1024);
						var read = _socket.input.readBytes(data, 0, data.length);
						if (read <= 0){
							break;
						}
						Log.debug("Bytes read: " + read, id);
						_buffer.writeBytes(data.sub(0, read));
					}
				} catch (e:Dynamic) {
					#if cs

					needClose = true;
					if (Std.isOfType(e, cs.system.io.IOException)) {
						var ioex = cast(e, cs.system.io.IOException);
						if (Std.isOfType(ioex.GetBaseException(), cs.system.net.sockets.SocketException)) {
							var sockex = cast(ioex.GetBaseException(), cs.system.net.sockets.SocketException);
							needClose = !(sockex.SocketErrorCode == cs.system.net.sockets.SocketError.WouldBlock);
						}
					}
					#else

					needClose = !(e == 'Blocking' || (Std.isOfType(e, Error) && (e:Error).match(Error.Blocked)));

					#end
				}

				if (needClose == false) {
					handleData();
				}
			}
		}

		if (needClose == true) { // dont want to send the Close frame here
			if (state != State.Closed) {
				try {
					Log.debug("Closed", id);
					state = State.Closed;
					_socket.close();
				} catch (e:Dynamic) { }

				if (onclose != null) {
					onclose();
				}
			}
		}
	}

	public function sendHttpRequest(httpRequest:HttpRequest) {
		var data = httpRequest.build();

		Log.data(data, id);

		try {
			_socket.output.write(Bytes.ofString(data));
			_socket.output.flush();
		} catch (e:Dynamic) {
			if (onerror != null) {
				onerror(Std.string(e));
			}
			close();
		}
	}

	public function sendHttpResponse(httpResponse:HttpResponse) {
		var data = httpResponse.build();

		Log.data(data, id);

		_socket.output.write(Bytes.ofString(data));
		_socket.output.flush();
	}

	public function recvHttpRequest():HttpRequest {
		var response = _buffer.readLinesUntil("\r\n\r\n");

		if (response == null) {
			return null;
		}

		var httpRequest = new HttpRequest();
		for (line in response) {
			if (line == null || line == "") {
				break;
			}
			httpRequest.addLine(line);
		}

		Log.data(httpRequest.toString(), id);

		return httpRequest;
	}

	public function recvHttpResponse():HttpResponse {
		var response = _buffer.readLinesUntil("\r\n\r\n");

		if (response == null) {
			return null;
		}

		var httpResponse = new HttpResponse();
		for (line in response) {
			if (line == null || line == "") {
				break;
			}
			httpResponse.addLine(line);

		}

		Log.data(httpResponse.toString(), id);

		return httpResponse;
	}

	private inline function makeWSKeyResponse(key:String):String {
		return Base64.encode(Sha1.make(Bytes.ofString(key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11')));
	}
}
