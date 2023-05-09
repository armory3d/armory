package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasSetVisibleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	override function run(from: Int) {
		var element = inputs[1].get();
		var visible = inputs[2].get();

		var canvas = CanvasScript.getActiveCanvas();
		canvas.notifyOnReady(() -> {
			var e = canvas.getElement(element);
			if (e != null) e.visible = visible;
			runOutput(0);
		});
	}
#end
}
