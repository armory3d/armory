package armory.logicnode;

import armory.system.Event;

class SendGlobalEventNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		final name: String = inputs[1].get();
		final entries = Event.get(name);

		if (entries != null) {
			for (e in entries) e.onEvent();
		}

		runOutput(0);
	}
}
