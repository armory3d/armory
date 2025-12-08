package armory.logicnode;

import armory.system.Signal;
import iron.object.Object;

class SignalNode extends LogicNode {
	var signal: Signal = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Null<Signal> {
		var object: Object = inputs[0].get();
		var property: String = inputs[1].get();

		if (object != null && property != null && property != "") {
			return Reflect.getProperty(object, property);
		}

		if (signal == null) {
			signal = new Signal();
		}
		return signal;
	}
}
