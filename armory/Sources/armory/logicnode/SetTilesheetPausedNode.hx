package armory.logicnode;

import iron.object.MeshObject;

class SetTilesheetPausedNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: MeshObject = inputs[1].get();
		var paused: Bool = inputs[2].get();

		if (object == null || object.tilesheet == null) return;

		paused ? object.tilesheet.pause() : object.tilesheet.resume();

		runOutput(0);
	}
}
