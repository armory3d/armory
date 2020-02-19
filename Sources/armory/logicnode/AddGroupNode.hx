package armory.logicnode;

import kha.arrays.Float32Array;

class AddGroupNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var groupName: String = inputs[1].get();
		var raw = iron.Scene.active.raw;

		// Already exists
		for (g in raw.groups) {
			if (g.name == groupName) {
				runOutput(0);
				return;
			}
		}

		raw.groups.push({ name: groupName, object_refs: [], instance_offset: new Float32Array(3)});
		runOutput(0);
	}
}
