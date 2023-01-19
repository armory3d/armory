package armory.logicnode;
import armory.system.Event;
import armory.network.Connect;
import iron.object.Object;


class NetworkEventNode extends LogicNode {
	public var property0: String;
	public var property1: String;

	public var value: String;
	public var listener: TEvent = null;
	public var net_Url: String;

	public function new(tree:LogicTree) {
		super(tree);
		tree.notifyOnInit(init);
	}

	function init() {
		if (property0 == "client") {
				net_Url = inputs[0].get();
				switch (property1) {
					case "onopen": value = Client.onOpenEvent;listener = Event.add(value, onEvent, tree.object.uid);
					case "onmessage": value = Client.onMessageEvent;listener = Event.add(value, onEvent, tree.object.uid);
					case "onerror": value = Client.onErrorEvent;listener = Event.add(value, onEvent, tree.object.uid);
					case "onclose": value = Client.onCloseEvent;listener = Event.add(value, onEvent, tree.object.uid);
		            default: throw "Failed to set client event type.";
				}
		} else if (property0 == "host") {
			#if sys
				var net_Domain = inputs[0].get();
				var net_Port = inputs[1].get();
				net_Url = "ws://" + net_Domain + ":" + Std.string(net_Port);
				switch (property1) {
					case "onopen": value = Host.onOpenEvent;listener = Event.add(value, onEvent, tree.object.uid);
					case "onmessage": value = Host.onMessageEvent;listener = Event.add(value, onEvent, tree.object.uid);
					case "onerror": value = Host.onErrorEvent;listener = Event.add(value, onEvent, tree.object.uid);
					case "onclose": value = Host.onCloseEvent;listener = Event.add(value, onEvent, tree.object.uid);
		            default: throw "Failed to set host event type.";
				}
			#end
		} else if (property0 == "securehost"){
			#if sys
				var net_Domain = inputs[0].get();
				var net_Port = inputs[1].get();
				net_Url = "wss://" + net_Domain + ":" + Std.string(net_Port);
				switch (property1) {
					case "onopen": value = SecureHost.onOpenEvent;listener = Event.add(value, onEvent, tree.object.uid);
					case "onmessage": value = SecureHost.onMessageEvent;listener = Event.add(value, onEvent, tree.object.uid);
					case "onerror": value = SecureHost.onErrorEvent;listener = Event.add(value, onEvent, tree.object.uid);
					case "onclose": value = SecureHost.onCloseEvent;listener = Event.add(value, onEvent, tree.object.uid);
		            default: throw "Failed to set host event type.";
 				}
			#end	
		}
		
	}

	function onEvent() {
		runOutput(0);
	}

	override function get(from: Int): Dynamic {
		if (property0 == "host") {
			return switch (from) {
				case 1: Host.id[net_Url];
				case 2: Host.data[net_Url];
				default: throw "Unreachable";
			}
		} 
		else if (property0 == "securehost") {
			return switch (from) {
				case 1: SecureHost.id[net_Url];
				case 2: SecureHost.data[net_Url];
				default: throw "Unreachable";
			}
		} 
		else {
			return switch (from) {
				case 1: Client.id[net_Url];
				case 2: Client.data[net_Url];
				default: throw "Unreachable";
			}
		}
	}

}
