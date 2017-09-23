package armory.logicnode;

import armory.object.MeshObject;

class PlayTilesheetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:MeshObject = inputs[1].get();
		var action:String = inputs[2].get();
		
		if (object == null) return;

		object.tilesheet.play(action, function() {
			runOutputs(1);
		});

		runOutputs(0);
	}
}
