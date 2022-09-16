package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasGetScaleNode extends LogicNode {

	var width: Int;
	var height: Int;

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

			height = e.height;
			width = e.width;
			runOutput(0);
		});
	}

	override function get(from: Int): Dynamic {
		if (from == 1) return height;
		else if (from == 2) return width;
		else return 0;
	}
#end
}
