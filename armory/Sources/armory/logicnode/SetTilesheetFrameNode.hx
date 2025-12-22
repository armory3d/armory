package armory.logicnode;

import iron.object.MeshObject;

class SetTilesheetFrameNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: MeshObject = inputs[1].get();
		var frame: Int = inputs[2].get();

		if (object == null) return;

		object.tilesheet.setFrameOffset(frame);

		runOutput(0);
	}
}
