package armory.logicnode;

import iron.object.Object;
import armory.system.Event;

class SendEventNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var name: String = inputs[1].get();
		var object: Object = inputs.length > 2 ? inputs[2].get() : tree.object;

		if (object == null) return;

		var entries = Event.get(name);
		if (entries == null) return;
		for (e in entries) if (e.mask == object.uid) e.onEvent();

		runOutput(0);
	}
}
