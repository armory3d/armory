package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;
import kha.Color;

@:deprecated("The 'Set Canvas Text Color' node is deprecated and will be removed in future SDK versions. Please use 'Set Canvas Color' instead.")
class CanvasSetTextColorNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	override function run(from: Int) {
		var element = inputs[1].get();
		var r = inputs[2].get();
		var g = inputs[3].get();
		var b = inputs[4].get();
		var a = inputs[5].get();

		var canvas = CanvasScript.getActiveCanvas();
		canvas.notifyOnReady(() -> {
			var e = canvas.getElement(element);
			if (e != null) e.color_text = Color.fromFloats(r, g, b, a);
			runOutput(0);
		});
	}
#end
}
