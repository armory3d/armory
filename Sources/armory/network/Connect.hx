package armory.network;

#if sys
import armory.network.WebSocketServer;
import armory.network.WebSocketSecureServer;
import sys.ssl.Key;
import sys.ssl.Certificate;
import armory.network.SocketImpl;
#end
import armory.network.WebSocket;
import armory.network.Types;
import haxe.io.Bytes;
import iron.object.Object;
import armory.system.Event;

class Connect {}

class Client extends Connect {

	public static var onOpenEvent: String = "Client.onOpen";
	public static var onMessageEvent: String = "Client.onMessage";
	public static var onErrorEvent: String = "Client.onError";
	public static var onCloseEvent: String = "Client.onClose";
	public static var connections:Map<String, armory.network.WebSocket> = [];
	public static var data:Map<String, Dynamic> = [];
	public static var id:Map<String, String> = [];

	public function new(net_Url: String, net_object: Object) {
		if (net_Url != null && net_object != null) {

			if (Client.connections[net_Url] == null) {

				var object = net_object;

				try {
					Client.connections[net_Url] = new armory.network.WebSocket(net_Url);
				}
				catch (error) {
					trace(error);
					return;
				}

				if (object != null) {
					final openEvent = Event.get(Client.onOpenEvent);
					final messageEvent = Event.get(Client.onMessageEvent);
					final errorEvent = Event.get(Client.onErrorEvent);
					final closeEvent = Event.get(Client.onCloseEvent);

					Client.connections[net_Url].onopen = function() {
						Client.data[net_Url] = "Connection open.";
						Client.id[net_Url] = Util.generateUUID();
						if (openEvent != null) {
							for (e in openEvent) {
								if (e.mask == object.uid) {
									e.onEvent();
								}
							}
						}
					}

					Client.connections[net_Url].onmessage = function(message: MessageType) {
						switch (message) {
							case BytesMessage(content):
								Client.data[net_Url] = content;
								if (messageEvent != null) {
									for (e in messageEvent) {
										if (e.mask == object.uid) {
											e.onEvent();
										}
									}
								}
							case StrMessage(content):
								Client.data[net_Url] = content;
								if (messageEvent != null) {
									for (e in messageEvent) {
										if (e.mask == object.uid) {
											e.onEvent();
										}
									}
								}
						}
					}

					Client.connections[net_Url].onerror = function(err) {
						Client.data[net_Url] = err;
						if (errorEvent != null) {
							for (e in errorEvent) {
								if (e.mask == object.uid) {
									e.onEvent();
								}
							}
						}
					}

					Client.connections[net_Url].onclose = function() {
						Client.data[net_Url] = "Connection closed.";
						if (closeEvent != null) {
							for (e in closeEvent) {
								if (e.mask == object.uid) {
									e.onEvent();
								}
							}
						}
					}
				}
			}
		}
	}
}

class Host extends Connect {

	public static var onOpenEvent: String = "Host.onOpen";
	public static var onMessageEvent: String = "Host.onMessage";
	public static var onErrorEvent: String = "Host.onError";
	public static var onCloseEvent: String = "Host.onClose";
	public static var object: Object = null;
	#if sys
		public static var connections:Map<String, WebSocketServer<HostHandler>> = [];
	#else
		public static var connections = null;
	#end
	public static var data:Map<String, Dynamic> = [];
	public static var id:Map<String, String> = [];
	public static var net_Url: String;

	public function new(net_Domain:String, net_Port:Int, net_Max:Int, net_object:Object) {

		if (net_object == null) return;

		object = net_object;
		net_Url = "ws://" + net_Domain + ":" + net_Port;

		#if sys
			if (connections[net_Url] != null) return;
			connections[net_Url] = new WebSocketServer<HostHandler>(net_Domain, net_Port, net_Max);
		#end
	}
}

#if sys
class HostHandler extends WebSocketHandler {

	public function new(s: SocketImpl) {
		super(s);

		if (Host.object != null) {
			final openEvent = Event.get(Host.onOpenEvent);
			final messageEvent = Event.get(Host.onMessageEvent);
			final errorEvent = Event.get(Host.onErrorEvent);
			final closeEvent = Event.get(Host.onCloseEvent);
			onopen = function() {
				Host.id[Host.net_Url] = id;
				if (openEvent != null) {
					for (e in openEvent) {
						if (e.mask == Host.object.uid) {
							e.onEvent();
						}
					}
				}
			}
			onmessage = function(message: MessageType) {
				switch (message) {
					case BytesMessage(content):
						Host.data[Host.net_Url] = content;
						Host.id[Host.net_Url] = id;
						if (messageEvent != null) {
							for (e in messageEvent) {
								if (e.mask == Host.object.uid) {
									e.onEvent();
								}
							}
						}
					case StrMessage(content):
						Host.data[Host.net_Url] = content;
						Host.id[Host.net_Url] = id;
						if (messageEvent != null) {
							for (e in messageEvent) {
								if (e.mask == Host.object.uid) {
									e.onEvent();
								}
							}
						}
				}
			}
			onerror = function(error) {
				Host.data[Host.net_Url] = error;
				Host.id[Host.net_Url] = id;
				if (errorEvent != null) {
					for (e in errorEvent) {
						if (e.mask == Host.object.uid) {
							e.onEvent();
						}
					}
				}
			}
			onclose = function() {
				Host.id[Host.net_Url] = id;
				if (closeEvent != null) {
					for (e in closeEvent) {
						if (e.mask == Host.object.uid) {
							e.onEvent();
						}
					}
				}
			}
		}
	}
}
#end

class SecureHost extends Connect {

	public static var onOpenEvent: String = "SecureHost.onOpen";
	public static var onMessageEvent: String = "SecureHost.onMessage";
	public static var onErrorEvent: String = "SecureHost.onError";
	public static var onCloseEvent: String = "SecureHost.onClose";
	public static var object: Object = null;
	public static var net_Url: String;
	#if sys
		public static var connections:Map<String, WebSocketSecureServer<SecureHostHandler>> = [];
	#else
		public static var connections = null;
	#end
	public static var data:Map<String, Dynamic> = [];
	public static var id:Map<String, String> = [];

	public function new(net_Domain:String, net_Port:Int, net_Max:Int, net_object:Object, net_Cert: String, net_Key: String) {
		if (net_object == null) return;

		object = net_object;

		net_Url = "wss://" + net_Domain + ":" + net_Port;

		#if sys
			var cert = Certificate.loadFile(net_Cert);
			var key = Key.loadFile(net_Key);
			if (connections[net_Url] != null) return;
			connections[net_Url] = new WebSocketSecureServer<SecureHostHandler>(net_Domain, net_Port, cert, key, cert, net_Max);
		#end
	}
}

#if sys
class SecureHostHandler extends WebSocketHandler {

	public function new(s: SocketImpl) {
		super(s);

		if (SecureHost.object != null) {
			final openEvent = Event.get(SecureHost.onOpenEvent);
			final messageEvent = Event.get(SecureHost.onMessageEvent);
			final errorEvent = Event.get(SecureHost.onErrorEvent);
			final closeEvent = Event.get(SecureHost.onCloseEvent);
			onopen = function() {
				SecureHost.id[SecureHost.net_Url] = id;
				if (openEvent != null) {
					for (e in openEvent) {
						if (e.mask == SecureHost.object.uid) {
							e.onEvent();
						}
					}
				}
			}
			onmessage = function(message: MessageType) {
				switch (message) {
					case BytesMessage(content):
						SecureHost.data[SecureHost.net_Url] = content;
						SecureHost.id[SecureHost.net_Url] = id;
						send(content);
						if (messageEvent != null) {
							for (e in messageEvent) {
								if (e.mask == SecureHost.object.uid) {
									e.onEvent();
								}
							}
						}
					case StrMessage(content):
						SecureHost.data[SecureHost.net_Url] = content;
						SecureHost.id[SecureHost.net_Url] = id;
						send(content);
						if (messageEvent != null) {
							for (e in messageEvent) {
								if (e.mask == SecureHost.object.uid) {
									e.onEvent();
								}
							}
						}
				}
			}
			onerror = function(error) {
				SecureHost.data[SecureHost.net_Url] = error;
				SecureHost.id[SecureHost.net_Url] = id;
				if (errorEvent != null) {
					for (e in errorEvent) {
						if (e.mask == SecureHost.object.uid) {
							e.onEvent();
						}
					}
				}
			}
			onclose = function() {
				SecureHost.id[SecureHost.net_Url] = id;
				if (closeEvent != null) {
					for (e in closeEvent) {
						if (e.mask == SecureHost.object.uid) {
							e.onEvent();
						}
					}
				}
			}
		}
	}
}
#end
