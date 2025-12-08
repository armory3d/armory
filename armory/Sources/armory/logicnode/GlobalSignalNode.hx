package armory.logicnode;

import armory.system.Signal;

class GlobalSignalNode extends LogicNode {
	public static var signals: Map<String, Signal> = new Map<String, Signal>();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Null<Signal> {
		var name: String = inputs[0].get();
		if (name == null || name == "")
			return null;

		var signal: Signal = signals.get(name);
		if (signal == null) {
			signal = new Signal();
			signals.set(name, signal);
		}
		return signal;
	}
}
