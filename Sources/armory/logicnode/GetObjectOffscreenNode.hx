package armory.logicnode;

import iron.object.Object;

class GetObjectOffscreenNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();

		if (object == null) return null;

		return switch (from) {
			case 0: object.culled;
			case 1: object.culledMesh;
			case 2: object.culledShadow;
			default: null;
		}

	}
}
