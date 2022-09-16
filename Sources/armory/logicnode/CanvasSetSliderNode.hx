package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasSetSliderNode extends LogicNode {

	var canvas: CanvasScript;
	var element: String;
	var value: Float;

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	function update() {
		if (!canvas.ready) return;

		// This Try/Catch hacks around an issue where the handles are
		// not created yet, even though canvas.ready is true.
		try {
			canvas.getHandle(element).value = value;
			tree.removeUpdate(update);
		}
		catch (e: Dynamic) {}

		runOutput(0);
	}

	override function run(from: Int) {
		element = inputs[1].get();
		value = inputs[2].get();

		canvas = CanvasScript.getActiveCanvas();

		// Ensure canvas is ready
		tree.notifyOnUpdate(update);
		update();
	}
#end
}
