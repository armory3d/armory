package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;
import kha.Color;
import iron.math.Vec4;

class CanvasSetProgressBarColorNode extends LogicNode {

	var canvas: CanvasScript;
	var element: String;
	var color = new Vec4();
	
	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	function update() {
		if (!canvas.ready) return;
		tree.removeUpdate(update);

		var e = canvas.getElement(element);
		if (e != null) e.color_progress = Color.fromFloats(color.x, color.y, color.z, color.w);
		runOutput(0);
	}

	override function run(from: Int) {
		element = inputs[1].get();
		color = inputs[2].get();
		canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);

		// Ensure canvas is ready
		tree.notifyOnUpdate(update);
		update();
	}
#end
}
