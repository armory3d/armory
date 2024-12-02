package armory.logicnode;
import iron.object.Object;
import armory.system.Event;
import armory.network.Types;
import armory.network.Util;
import armory.network.Connect;


class NetworkClientNode extends LogicNode {
		public var net_Url: String;
		public var data: Dynamic;
		public var client: armory.network.WebSocket;

		public function new(tree:LogicTree) {
				super(tree);
		}

		override function run(from:Int) {
				net_Url = inputs[1].get();
				if (net_Url == null) return;
				if(Client.connections[net_Url] == null){
						var object = tree.object;
						var client = new armory.network.Connect.Client(net_Url, object);
				} else {
						return;
				}
				runOutput(0);
		}

	override function get(from: Int): Dynamic {
	    return Client.connections[net_Url];
	}

}
