package armory.logicnode;

import iron.object.MeshObject;

class SetTilesheetPausedNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: MeshObject = inputs[1].get();
		var enabled: Bool = inputs[2].get();

		if (object == null) return;

		enabled ? object.tilesheet.resume() : object.tilesheet.pause();

		runOutput(0);
	}
}
