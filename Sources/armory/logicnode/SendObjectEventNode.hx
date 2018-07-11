package armory.logicnode;

import iron.object.Object;
import armory.system.Event;

class SendObjectEventNode extends LogicNode {

	var entries:Array<TEvent> = null;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var name:String = inputs[2].get();
		
		if (object == null) return null;

		// if (entries == null) {
			var all = Event.get(name);
			if (all != null) {
				entries = [];
				for (e in all) if (e.mask == object.uid) entries.push(e);
			}
		// }
		if (entries == null) return;
		for (e in entries) e.onEvent();

		super.run();
	}
}
