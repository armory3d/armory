package armory.logicnode;

import iron.object.Object;
import armory.system.Event;

class SendEventNode extends LogicNode {

	var entries:Array<TEvent> = null;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var name:String = inputs[1].get();
		
		// if (entries == null) {
			var all = Event.get(name);
			if (all != null) {
				entries = [];
				for (e in all) if (e.mask == tree.object.uid) entries.push(e);
			}
		// }
		if (entries == null) return;
		for (e in entries) e.onEvent();

		super.run();
	}
}
