package armory.logicnode;
import armory.network.Connect;
import armory.network.Buffer;
import haxe.io.Bytes;
import iron.object.Object;
import iron.math.Vec4;
import iron.math.Quat;
import iron.math.Mat4;


class NetworkSendMessageNode extends LogicNode {
	public var property0: String;
	public var property1: String;
	public var id: String;
	public var all: Bool;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
    	var api: String = inputs[2].get();
		var message: Dynamic = inputs[3].get();
		if (message == null) return;

        switch (property1) {
            case "string":
				if(property0 == "client"){
					var connection = cast(inputs[1].get(), armory.network.WebSocket);
					var buffer = new Buffer();
					buffer.writeBytes(Bytes.ofString(message));
					if(api != "" || api != null){
						buffer.writeBytes(Bytes.ofString(api));
					}
					try {
						connection.send(buffer);
					} catch(error) {
						trace("Error: " + error);
					}
				} 
				#if sys
				else if(inputs[5].get() == true){
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							var buffer = new Buffer();
							buffer.writeBytes(Bytes.ofString(message));
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							var buffer = new Buffer();
							buffer.writeBytes(Bytes.ofString(message));
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}
					}
				} else {
					var id = inputs[4].get();
					if (id == null) return;
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var buffer = new Buffer();
								buffer.writeBytes(Bytes.ofString(message));
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var buffer = new Buffer();
								buffer.writeBytes(Bytes.ofString(message));
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					}
				} 
				#end
				runOutput(0);
            case "vector":   
				if(property0 == "client"){
					var connection = cast(inputs[1].get(), armory.network.WebSocket);
					var bytesOut = new haxe.io.BytesOutput();
					var i = Reflect.fields(message);
					for (b in i) {
						bytesOut.writeFloat(Reflect.field(message, b));
					}
					var buffer = new Buffer();
					buffer.writeBytes(bytesOut.getBytes());
					if(api != "" || api != null){
						buffer.writeBytes(Bytes.ofString(api));
					}
					try {
						connection.send(buffer);
					} catch(error) {
						trace("Error: " + error);
					}
				} 
				#if sys
				else if(inputs[5].get() == true){
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							var bytesOut = new haxe.io.BytesOutput();
							var i = Reflect.fields(message);
							for (b in i) {
								bytesOut.writeFloat(Reflect.field(message, b));
							}
							var buffer = new Buffer();
							buffer.writeBytes(bytesOut.getBytes());
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							var bytesOut = new haxe.io.BytesOutput();
							var i = Reflect.fields(message);
							for (b in i) {
								bytesOut.writeFloat(Reflect.field(message, b));
							}
							var buffer = new Buffer();
							buffer.writeBytes(bytesOut.getBytes());
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}
					}
				} else {
					var id = inputs[4].get();
					if (id == null) return;
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var bytesOut = new haxe.io.BytesOutput();
								var i = Reflect.fields(message);
								for (b in i) {
									bytesOut.writeFloat(Reflect.field(message, b));
								}
								var buffer = new Buffer();
								buffer.writeBytes(bytesOut.getBytes());
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var bytesOut = new haxe.io.BytesOutput();
								var i = Reflect.fields(message);
								for (b in i) {
									bytesOut.writeFloat(Reflect.field(message, b));
								}
								var buffer = new Buffer();
								buffer.writeBytes(bytesOut.getBytes());
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					}
				} 
				#end
				runOutput(0);
            case "float":   
				if(property0 == "client"){
					var connection = cast(inputs[1].get(), armory.network.WebSocket);
					var bytesOut = new haxe.io.BytesOutput();
					bytesOut.writeFloat(message);
				    var buffer = new Buffer();
				    buffer.writeBytes(bytesOut.getBytes());
					if(api != "" || api != null){
						buffer.writeBytes(Bytes.ofString(api));
					}
					try {
						connection.send(buffer);
					} catch(error) {
						trace("Error: " + error);
					}
				} 
				#if sys
				else if(inputs[5].get() == true){
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							var bytesOut = new haxe.io.BytesOutput();
							bytesOut.writeFloat(message);
						    var buffer = new Buffer();
						    buffer.writeBytes(bytesOut.getBytes());
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							var bytesOut = new haxe.io.BytesOutput();
							bytesOut.writeFloat(message);
						    var buffer = new Buffer();
						    buffer.writeBytes(bytesOut.getBytes());
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}
					}
				} else {
					var id = inputs[4].get();
					if (id == null) return;
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var bytesOut = new haxe.io.BytesOutput();
								bytesOut.writeFloat(message);
						        var buffer = new Buffer();
						        buffer.writeBytes(bytesOut.getBytes());
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var bytesOut = new haxe.io.BytesOutput();
								bytesOut.writeFloat(message);
						        var buffer = new Buffer();
						        buffer.writeBytes(bytesOut.getBytes());
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					}
				} 
				#end
				runOutput(0);
            case "integer":  
				if(property0 == "client"){
					var connection = cast(inputs[1].get(), armory.network.WebSocket);
					var bytesOut = new haxe.io.BytesOutput();
				    bytesOut.writeInt32(message);
					var buffer = new Buffer();
				    buffer.writeBytes(bytesOut.getBytes());
					if(api != "" || api != null){
						buffer.writeBytes(Bytes.ofString(api));
					}
					try {
						connection.send(buffer);
					} catch(error) {
						trace("Error: " + error);
					}
				} 
				#if sys
				else if(inputs[5].get() == true){
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							var bytesOut = new haxe.io.BytesOutput();
						    bytesOut.writeInt32(message);
							var buffer = new Buffer();
						    buffer.writeBytes(bytesOut.getBytes());
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							var bytesOut = new haxe.io.BytesOutput();
						    bytesOut.writeInt32(message);
							var buffer = new Buffer();
						    buffer.writeBytes(bytesOut.getBytes());
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}
					}
				} else {
					var id = inputs[4].get();
					if (id == null) return;
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var bytesOut = new haxe.io.BytesOutput();
								bytesOut.writeInt32(message);
								var buffer = new Buffer();
						        buffer.writeBytes(bytesOut.getBytes());
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var bytesOut = new haxe.io.BytesOutput();
								bytesOut.writeInt32(message);
								var buffer = new Buffer();
						        buffer.writeBytes(bytesOut.getBytes());
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					}
				} 
				#end
				runOutput(0);
            case "boolean":  
				if(property0 == "client"){
					var connection = cast(inputs[1].get(), armory.network.WebSocket);
					var buffer = new Buffer();
					if(message == true){
						buffer.writeBytes(Bytes.ofString("true"));
					} else {
						buffer.writeBytes(Bytes.ofString("false"));
					}
					if(api != "" || api != null){
						buffer.writeBytes(Bytes.ofString(api));
					}
					try {
						connection.send(buffer);
					} catch(error) {
						trace("Error: " + error);
					}
				} 
				#if sys
				else if(inputs[5].get() == true){
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							var buffer = new Buffer();
							if(message == true){
								buffer.writeBytes(Bytes.ofString("true"));
							} else {
								buffer.writeBytes(Bytes.ofString("false"));
							}
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							var buffer = new Buffer();
							if(message == true){
								buffer.writeBytes(Bytes.ofString("true"));
							} else {
								buffer.writeBytes(Bytes.ofString("false"));
							}
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}
					}
				} else {
					var id = inputs[4].get();
					if (id == null) return;
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var buffer = new Buffer();
								if(message == true){
									buffer.writeBytes(Bytes.ofString("true"));
								} else {
									buffer.writeBytes(Bytes.ofString("false"));
								}
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var buffer = new Buffer();
								if(message == true){
									buffer.writeBytes(Bytes.ofString("true"));
								} else {
									buffer.writeBytes(Bytes.ofString("false"));
								}
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					}
				} 
				#end
				runOutput(0);
            case "transform":
				if(property0 == "client"){
					var connection = cast(inputs[1].get(), armory.network.WebSocket);
					var bytesOut = new haxe.io.BytesOutput();
					var transform:Mat4 = message;
					var loc = new Vec4();
					var rot = new Quat();
					var scale = new Vec4();
					transform.decompose(loc, rot, scale);
					var l = Reflect.fields(loc);
					for (b in l) {
						bytesOut.writeFloat(Reflect.field(loc, b));
					}
					var r = Reflect.fields(rot);
					for (b in r) {
						bytesOut.writeFloat(Reflect.field(rot, b));
					}
					var s = Reflect.fields(scale);
					for (b in s) {
						bytesOut.writeFloat(Reflect.field(scale, b));
					}
				    var buffer = new Buffer();
				    buffer.writeBytes(bytesOut.getBytes());
					if(api != "" || api != null){
						buffer.writeBytes(Bytes.ofString(api));
					}
					try {
						connection.send(buffer);
					} catch(error) {
						trace("Error: " + error);
					}
				} 
				#if sys
				else if(inputs[5].get() == true){
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							var bytesOut = new haxe.io.BytesOutput();
							var transform:Mat4 = message;
							var loc = new Vec4();
							var rot = new Quat();
							var scale = new Vec4();
							transform.decompose(loc, rot, scale);
							var l = Reflect.fields(loc);
							for (b in l) {
								bytesOut.writeFloat(Reflect.field(loc, b));
							}
							var r = Reflect.fields(rot);
							for (b in r) {
								bytesOut.writeFloat(Reflect.field(rot, b));
							}
							var s = Reflect.fields(scale);
							for (b in s) {
								bytesOut.writeFloat(Reflect.field(scale, b));
							}
						    var buffer = new Buffer();
						    buffer.writeBytes(bytesOut.getBytes());
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							var bytesOut = new haxe.io.BytesOutput();
							var transform:Mat4 = message;
							var loc = new Vec4();
							var rot = new Quat();
							var scale = new Vec4();
							transform.decompose(loc, rot, scale);
							var l = Reflect.fields(loc);
							for (b in l) {
								bytesOut.writeFloat(Reflect.field(loc, b));
							}
							var r = Reflect.fields(rot);
							for (b in r) {
								bytesOut.writeFloat(Reflect.field(rot, b));
							}
							var s = Reflect.fields(scale);
							for (b in s) {
								bytesOut.writeFloat(Reflect.field(scale, b));
							}
						    var buffer = new Buffer();
						    buffer.writeBytes(bytesOut.getBytes());
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}					
					}
				} else {
					var id = inputs[4].get();
					if (id == null) return;
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var bytesOut = new haxe.io.BytesOutput();
								var transform:Mat4 = message;
								var loc = new Vec4();
								var rot = new Quat();
								var scale = new Vec4();
								transform.decompose(loc, rot, scale);
								var l = Reflect.fields(loc);
								for (b in l) {
									bytesOut.writeFloat(Reflect.field(loc, b));
								}
								var r = Reflect.fields(rot);
								for (b in r) {
									bytesOut.writeFloat(Reflect.field(rot, b));
								}
								var s = Reflect.fields(scale);
								for (b in s) {
									bytesOut.writeFloat(Reflect.field(scale, b));
								}
								var buffer = new Buffer();
								buffer.writeBytes(bytesOut.getBytes());
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var bytesOut = new haxe.io.BytesOutput();
								var transform:Mat4 = message;
								var loc = new Vec4();
								var rot = new Quat();
								var scale = new Vec4();
								transform.decompose(loc, rot, scale);
								var l = Reflect.fields(loc);
								for (b in l) {
									bytesOut.writeFloat(Reflect.field(loc, b));
								}
								var r = Reflect.fields(rot);
								for (b in r) {
									bytesOut.writeFloat(Reflect.field(rot, b));
								}
								var s = Reflect.fields(scale);
								for (b in s) {
									bytesOut.writeFloat(Reflect.field(scale, b));
								}
								var buffer = new Buffer();
								buffer.writeBytes(bytesOut.getBytes());
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					}
				} 
				#end
				runOutput(0);
            case "rotation": 
				if(property0 == "client"){
					var connection = cast(inputs[1].get(), armory.network.WebSocket);
					var bytesOut = new haxe.io.BytesOutput();
					var i = Reflect.fields(message);
					for (b in i) {
						bytesOut.writeFloat(Reflect.field(message, b));
					}
					var buffer = new Buffer();
					buffer.writeBytes(bytesOut.getBytes());
					if(api != "" || api != null){
						buffer.writeBytes(Bytes.ofString(api));
					}
					try {
						connection.send(buffer);
					} catch(error) {
						trace("Error: " + error);
					}
				} 
				#if sys
				else if(inputs[5].get() == true){
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							var bytesOut = new haxe.io.BytesOutput();
							var i = Reflect.fields(message);
							for (b in i) {
								bytesOut.writeFloat(Reflect.field(message, b));
							}
							var buffer = new Buffer();
							buffer.writeBytes(bytesOut.getBytes());
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							var bytesOut = new haxe.io.BytesOutput();
							var i = Reflect.fields(message);
							for (b in i) {
								bytesOut.writeFloat(Reflect.field(message, b));
							}
							var buffer = new Buffer();
							buffer.writeBytes(bytesOut.getBytes());
							if(api != "" || api != null){
								buffer.writeBytes(Bytes.ofString(api));
							}
							try {
								h.send(buffer);
							} catch(error) {
								trace("Error: " + error);
							}
						}					
					}
				} else {
					var id = inputs[4].get();
					if (id == null) return;
					if(property0 == "securehost"){
						var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var bytesOut = new haxe.io.BytesOutput();
								var i = Reflect.fields(message);
								for (b in i) {
									bytesOut.writeFloat(Reflect.field(message, b));
								}
								var buffer = new Buffer();
								buffer.writeBytes(bytesOut.getBytes());
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					} else {
						var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
						for(h in connection.handlers){
							if(h.id == id){
								var bytesOut = new haxe.io.BytesOutput();
								var i = Reflect.fields(message);
								for (b in i) {
									bytesOut.writeFloat(Reflect.field(message, b));
								}
								var buffer = new Buffer();
								buffer.writeBytes(bytesOut.getBytes());
								if(api != "" || api != null){
									buffer.writeBytes(Bytes.ofString(api));
								}
								try {
									h.send(buffer);
								} catch(error) {
									trace("Error: " + error);
								}
							}
						}
					}
				} 
				#end
				runOutput(0);
            default: throw "Failed to send data.";
        }

	}

}


