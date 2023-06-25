package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasSetLocationNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	override function run(from: Int) {
		var element = inputs[1].get();
		var newX = inputs[2].get();
		var newY = inputs[3].get();

		var canvas = CanvasScript.getActiveCanvas();
		canvas.notifyOnReady(() -> {
			var e = canvas.getElement(element);
			if (e != null) {
				e.x = newX;
				e.y = newY;
			}
			runOutput(0);
		});
	}
#end
}
