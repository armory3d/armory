package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasGetLocationNode extends LogicNode {

	var x: Float;
	var y: Float;

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

			x = e.x;
			y = e.y;
			runOutput(0);
		});
	}

	override function get(from: Int): Dynamic {
		if (from == 1) return x;
		else if (from == 2) return y;
		else return 0;
	}
#end
}
