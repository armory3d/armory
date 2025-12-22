package armory.logicnode;

import iron.Scene;
import iron.object.MeshObject;

class SetActiveTilesheetNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: MeshObject = inputs[1].get();
		var materialRef: String = inputs[2].get();
		var action: String = inputs[3].get();

		if (object == null) return;

		object.setActiveTilesheet(Scene.active.raw.name, materialRef, action);

		runOutput(0);
	}
}
