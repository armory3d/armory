package armory.logicnode;
import armory.system.Event;
import armory.network.Connect;
import iron.object.Object;


class NetworkCloseConnectionNode extends LogicNode {
	public var property0: Bool;
	public var property1: String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		if(property1 == "client") {
			var connection = cast(inputs[1].get(), armory.network.WebSocket);
	  		if (connection == null) return;
		    #if sys
		  		try{
		  			var net_Url = connection._protocol + "://" + connection._host + ":" + connection._port;
   			    	connection.close();
   			    	if(property0 == true){
   			    		Client.connections[net_Url] = null;
   			    	} else {
   			    		Client.connections[net_Url] = connection;
   			    	}
   				} catch(error) {
   					trace("Error: " + error);
   					return;
   				}
		  	#else
		  		try{
			  		var net_Url = @:privateAccess connection._url;
   			    	connection.close();
   			    	if(property0 == true){
   			    		Client.connections[net_Url] = null;
   			    	} else {
   			    		Client.connections[net_Url] = connection;
   			    	}
   				} catch(error) {
   					trace("Error: " + error);
   					return;
   				}
		    #end
		} else if(property1 == "securehost"){
	        #if sys
				var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<armory.network.Connect.HostHandler>);
		  		if (connection == null) return;
	  			var net_Url = "wss://" + @:privateAccess connection._host + ":" + @:privateAccess connection._port;
	 		    if(SecureHost.connections[net_Url] != null){
			    	connection.stop();
			   		if(property0 == true){
		    			SecureHost.connections[net_Url] = null;
		    		}
				}
	        #end
		} else {
            #if sys
				var connection = cast(inputs[1].get(), armory.network.WebSocketServer<armory.network.Connect.HostHandler>);
		  		if (connection == null) return;
	  			var net_Url = "ws://" + @:privateAccess connection._host + ":" + @:privateAccess connection._port;
	 		    if(Host.connections[net_Url] != null){
			    	connection.stop();
			   		if(property0 == true){
		    			Host.connections[net_Url] = null;
		    		}
				}
	        #end
		}
		runOutput(0);
	}

}
