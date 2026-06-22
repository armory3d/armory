package armory.logicnode;

import kha.Color;
import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasSetColorNode extends LogicNode {

	public var property0: String; // Attribute

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	override function run(from: Int) {
		var elementName = inputs[1].get();
		var color: iron.math.Vec4 = inputs[2].get();

		var canvas = CanvasScript.getActiveCanvas();
		canvas.notifyOnReady(() -> {
			var element = canvas.getElement(elementName);
			var c = Color.fromFloats(color.x, color.y, color.z, color.w);

			if (element != null) {
				switch (property0) {
					case "color": element.color = c;
					case "color_text": element.color_text = c;
					case "color_hover": element.color_hover = c;
					case "color_press": element.color_press = c;
					case "color_progress": element.color_progress = c;
				}
			}

			runOutput(0);
		});
	}
#end
}
