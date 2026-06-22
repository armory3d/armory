package armory.logicnode;

import iron.object.Object;
import armory.system.Event;

class SendEventNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		final name: String = inputs[1].get();
		final object: Object = inputs.length > 2 ? inputs[2].get() : tree.object;

		if (object != null) {
			final entries = Event.get(name);

			if (entries != null) {
				for (e in entries) if (e.mask == object.uid) e.onEvent();
			}
		}

		runOutput(0);
	}
}
