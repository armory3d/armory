package armory.logicnode;

import iron.object.MeshObject;

class ResumeTilesheetNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: MeshObject = inputs[1].get();

		if (object == null || object.tilesheet == null) return;

		object.tilesheet.resume();

		runOutput(0);
	}
}
