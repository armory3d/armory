package armory.logicnode;

import iron.object.Object;

class GetMeshVisibleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();

		if (object == null) return false;

		return object.visibleMesh;
	}
}
