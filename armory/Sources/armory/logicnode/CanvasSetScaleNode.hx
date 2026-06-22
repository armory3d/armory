package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasSetScaleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	override function run(from: Int) {
		var element = inputs[1].get();
		var height = inputs[2].get();
		var width = inputs[3].get();

		var canvas = CanvasScript.getActiveCanvas();
		canvas.notifyOnReady(() -> {
			var e = canvas.getElement(element);
			if (e != null) {
				e.height = height;
				e.width = width;
			}
			runOutput(0);
		});
	}
#end
}
