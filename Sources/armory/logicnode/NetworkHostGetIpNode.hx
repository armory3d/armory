package armory.logicnode;
import armory.network.Connect;
import iron.object.Object;


class NetworkHostGetIpNode extends LogicNode {
    public var property0: Bool;
	public var ip: String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		#if sys
			if(property0 == false){				
				var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
		  		if (connection == null) return;
				var id = inputs[2].get();
				if (id == null) return;
				for(h in connection.handlers){
					if(h.id == id){
						var p_ip = @:privateAccess h._socket.peer();
						ip = p_ip.host.toString();
					} 
				}
				runOutput(0);
			} else {
				var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
				if (connection == null) return;
				var id = inputs[2].get();
				if (id == null) return;
				for(h in connection.handlers){
					if(h.id == id){
						var p_ip = @:privateAccess h._socket.peer();
						ip = p_ip.host.toString();
					}
				}
	     		runOutput(0);
			}
		#end
	}

    override function get(from: Int): String {
        return ip;
    }
}


