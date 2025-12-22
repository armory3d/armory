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
			case 0: tilesheet.materialName;
			case 1: tilesheet.action != null ? tilesheet.action.name : null;
			case 2: tilesheet.getFrameOffset();
			case 3: tilesheet.frame;
			case 4: tilesheet.paused;
			default: null;
		}
	}
}
