package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasGetPBNode extends LogicNode {

	var at: Int;
	var max: Int;

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

			at = canvas.getElement(element).progress_at;
			max = canvas.getElement(element).progress_total;
			runOutput(0);
		});
	}

	override function get(from: Int): Dynamic {
		if (from == 1) return at;
		else if (from == 2) return max;
		else return 0;
	}
#end
}
