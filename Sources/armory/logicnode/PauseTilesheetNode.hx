package armory.logicnode;

import iron.object.MeshObject;

class PauseTilesheetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(node:LogicNode) {
		var object:MeshObject = inputs[1].get();
		
		if (object == null) return;

		object.tilesheet.pause();

		super.run(this);
	}
}
