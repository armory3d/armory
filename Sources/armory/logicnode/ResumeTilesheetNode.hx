package armory.logicnode;

import armory.object.MeshObject;

class ResumeTilesheetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:MeshObject = inputs[1].get();
		
		if (object == null) return;

		object.tilesheet.resume();

		super.run();
	}
}
