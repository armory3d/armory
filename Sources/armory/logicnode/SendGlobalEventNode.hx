package armory.logicnode;

import armory.system.Event;

class SendGlobalEventNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var name: String = inputs[1].get();

		var entries = Event.get(name);
		if (entries == null) return; // Event does not exist
		for (e in entries) e.onEvent();

		runOutput(0);
	}
}
