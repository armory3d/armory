package armory.logicnode;

import iron.object.Object;
import armory.system.Event;

class SendEventNode extends LogicNode {

	var entries:Array<TEvent> = null;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var name:String = inputs[1].get();
		var object:Object = inputs.length > 2 ? inputs[2].get() : tree.object;

		if (object == null) return null;
		
		var all = Event.get(name);
		if (all != null) {
			entries = [];
			for (e in all) if (e.mask == object.uid) entries.push(e);
		}
		if (entries == null) return;
		for (e in entries) e.onEvent();

		runOutput(0);
	}
}
