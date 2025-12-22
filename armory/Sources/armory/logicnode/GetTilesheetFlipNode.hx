package armory.logicnode;

import iron.object.MeshObject;

class GetTilesheetFlipNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: MeshObject = inputs[0].get();

		if (object == null) return null;
		if (object.tilesheet == null) return null;

		if (from == 0) return object.tilesheet.flipX;
		if (from == 1) return object.tilesheet.flipY;

		return null;
	}
}
