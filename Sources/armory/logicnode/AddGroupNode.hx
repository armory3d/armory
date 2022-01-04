package armory.logicnode;

import kha.arrays.Float32Array;
import iron.object.Object;

class AddGroupNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var groupName: String = inputs[1].get();
		var objects: Array<Object> = inputs[2].get();
		var raw = iron.Scene.active.raw;
		var object_names = [];

		// Already exists
		for (g in raw.groups) {
			if (g.name == groupName) {
				runOutput(0);
				return;
			}
		}

		if(objects != null) 
			for(o in objects)
				object_names.push(o.name);
		
		raw.groups.push({ name: groupName, object_refs: object_names, instance_offset: new Float32Array(3)});
		runOutput(0);
	}
}
