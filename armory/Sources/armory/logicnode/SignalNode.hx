package armory.logicnode;

import armory.system.Signal;

class SignalNode extends LogicNode {
	var standaloneSignal: Signal = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Dynamic = inputs[0].get();
		var property: String = inputs[1].get();

		if (object != null && property != null && property != "") {
			return Reflect.getProperty(object, property);
		}

		if (standaloneSignal == null) {
			standaloneSignal = new Signal();
		}
		return standaloneSignal;
	}
}
