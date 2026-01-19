package armory.logicnode;

import iron.object.MeshObject;

class SetTilesheetFlipNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: MeshObject = inputs[1].get();
		var flipX: Bool = inputs[2].get();
		var flipY: Bool = inputs[3].get();

		if (object == null) return;
		if (object.tilesheet == null) return;

		object.tilesheet.flipX = flipX;
		object.tilesheet.flipY = flipY;

		runOutput(0);
	}
}
