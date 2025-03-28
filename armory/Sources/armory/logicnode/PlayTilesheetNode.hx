package armory.logicnode;

import iron.object.MeshObject;

class PlayTilesheetNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: MeshObject = inputs[1].get();
		var action: String = inputs[2].get();

		if (object == null) return;

		object.activeTilesheet.play(action, function() {
			runOutput(1);
		});

		runOutput(0);
	}
}
