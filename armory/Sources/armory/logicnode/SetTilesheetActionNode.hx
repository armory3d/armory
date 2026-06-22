package armory.logicnode;

import iron.object.MeshObject;

class SetTilesheetActionNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: MeshObject = inputs[1].get();
		var action: String = inputs[2].get();

		if (object == null || object.tilesheet == null) return;

		object.setTilesheetAction(action);

		runOutput(0);
	}
}
