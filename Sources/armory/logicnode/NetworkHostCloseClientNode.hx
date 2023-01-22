package armory.logicnode;
import armory.network.Connect;
import iron.object.Object;


class NetworkHostCloseClientNode extends LogicNode {
    public var property0: Bool;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		#if sys
			if(property0 == false){
				var connection = cast(inputs[1].get(), armory.network.WebSocketServer<HostHandler>);
		  		if (connection == null) return;
				var id = inputs[2].get();
				for(h in connection.handlers){
					if(h.id == id){
						h.close();
					}
				}
	     		runOutput(0);
			} else {
				var connection = cast(inputs[1].get(), armory.network.WebSocketSecureServer<SecureHostHandler>);
		  		if (connection == null) return;
				var id = inputs[2].get();
				for(h in connection.handlers){
					if(h.id == id){
						h.close();
					}
				}
	     		runOutput(0);
			}
		#end
	}

}


