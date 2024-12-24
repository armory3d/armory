package armory.logicnode;
import armory.system.Event;
import armory.network.Connect;
import armory.network.Types;
import armory.network.Util;
import iron.object.Object;


class NetworkOpenConnectionNode extends LogicNode {
	public var property0: String;
	public var net_Url: String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		if(property0 == "client") {
			var connection = cast(inputs[1].get(), armory.network.WebSocket);
	  		if (connection == null) return;
	  		var object = tree.object;
	  		#if sys
		  		net_Url = connection._protocol + "://" + connection._host + ":" + connection._port;
		  		Client.connections[net_Url] = null;
        	var client = new armory.network.Connect.Client(net_Url, object);
		    #else
		  		net_Url = @:privateAccess connection._url;
		  		var client = Client.connections[net_Url];
		    	if (client == null) return;
					try {
	  				client.open();
		    	} catch (error) {
					trace("Error: " + error);
					return;
		    	}
				final openEvent = Event.get(Client.onOpenEvent);
				final messageEvent = Event.get(Client.onMessageEvent);
				final errorEvent = Event.get(Client.onErrorEvent);
				final closeEvent = Event.get(Client.onCloseEvent);
				client.onopen = function() {
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
				client.onmessage = function(message: MessageType) {
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
				client.onerror = function(err){    
				    Client.data[net_Url] = err;
				    if (errorEvent != null) {
				      for (e in errorEvent) {
				        if (e.mask == object.uid) {
				          e.onEvent();
				        }
				      }
				    }
				}
				client.onclose =function(){
				    Client.data[net_Url] = "Connection closed.";
				    if (closeEvent != null) {
				      for (e in closeEvent) {
				        if (e.mask == object.uid) {
				          e.onEvent();
				        }
				      }
				    }
				}
		    	Client.connections[net_Url] = client;
		  	#end
				runOutput(0);
		} else if (property0 == "securehost"){
        #if sys
			var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<armory.network.Connect.HostHandler>);
	  		if (connection == null) return;
		  	net_Url = "wss://" + @:privateAccess connection._host + ":" + @:privateAccess connection._port;
 		    if(SecureHost.connections[net_Url] != null){
 		    	try{
			    	connection.start();
			    }catch(error){
			    	trace("Error: " + error);
			    }
		  	}
  			runOutput(0);
	    #end
		} else {
      	#if sys
			var connection = cast(inputs[1].get(), armory.network.WebSocketServer<armory.network.Connect.HostHandler>);
	  		if (connection == null) return;
		  	net_Url = "ws://" + @:privateAccess connection._host + ":" + @:privateAccess connection._port;
 		    if(Host.connections[net_Url] != null){
		    	try{
		    	connection.start();
		    }catch(error){
		    	trace("Error: " + error);
		    }
	  		runOutput(0);
		  	}
	    #end
		}
	}

	override function get(from: Int): Dynamic {
		return switch (property0) {
			#if sys
			case "host": Host.connections[net_Url];
			case "securehost": SecureHost.connections[net_Url];
			#end 
			case "client": Client.connections[net_Url];
			default: throw "Unreachable";
		}
	}
}
