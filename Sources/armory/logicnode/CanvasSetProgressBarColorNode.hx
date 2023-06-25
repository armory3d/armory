package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;
import kha.Color;
import iron.math.Vec4;

@:deprecated("The 'Set Canvas Progress Bar Color' node is deprecated and will be removed in future SDK versions. Please use 'Set Canvas Color' instead.")
class CanvasSetProgressBarColorNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	override function run(from: Int) {
		var element = inputs[1].get();
		var color: Vec4 = inputs[2].get();

		var canvas = CanvasScript.getActiveCanvas();
		canvas.notifyOnReady(() -> {
			var e = canvas.getElement(element);
			if (e != null) e.color_progress = Color.fromFloats(color.x, color.y, color.z, color.w);
			runOutput(0);
		});
	}
#end
}
