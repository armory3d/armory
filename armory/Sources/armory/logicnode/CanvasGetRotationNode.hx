package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasGetRotationNode extends LogicNode {

	var rad: Float;

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	override function run(from: Int) {
		var element = inputs[1].get();

		var canvas = CanvasScript.getActiveCanvas();
		canvas.notifyOnReady(() -> {
			var e = canvas.getElement(element);
			if (e == null) return;

			rad = e.rotation;
			runOutput(0);
		});
	}

	override function get(from: Int): Dynamic {
		if (from == 1) return rad;
		else return 0;
	}
#end
}
