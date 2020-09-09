package armory.logicnode;

import iron.object.Object;

class SetMeshVisibleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var visible: Bool = inputs[2].get();

		if (object == null) return;

		object.visibleMesh = visible;

		runOutput(0);
	}
}
