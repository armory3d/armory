package armory.logicnode;

import iron.object.MeshObject;

class GetTilesheetStateNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: MeshObject = inputs[0].get();

		if (object == null) return null;

		var tilesheet = object.activeTilesheet;

		return switch (from) {
			case 0: tilesheet.raw.name;
			case 1: tilesheet.action.name;
			case 2: tilesheet.getFrameOffset();
			case 3: tilesheet.frame;
			case 4: tilesheet.paused;
			default: null;
		}
	}
}
