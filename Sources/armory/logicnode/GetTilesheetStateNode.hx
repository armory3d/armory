package armory.logicnode;

import iron.object.MeshObject;

class GetTilesheetStateNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: MeshObject = inputs[0].get();

		if (object == null) return null;

		var tilesheet = object.tilesheet;

		return switch (from) {
			case 0: tilesheet.action.name;
			case 1: tilesheet.frame;
			case 2: tilesheet.paused;
			default: null;
		}
	}
}
