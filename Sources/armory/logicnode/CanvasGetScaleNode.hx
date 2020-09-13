package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasGetScaleNode extends LogicNode {

	var canvas: CanvasScript;
	var element: String;
	var width: Int;
	var height: Int;

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	function update() {
		if (!canvas.ready) return;
		tree.removeUpdate(update);

		var e = canvas.getElement(element);
		if (e == null) return;

		height = e.height;
		width = e.width;
		runOutput(0);
	}

	override function run(from: Int) {
		element = inputs[1].get();
		canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);

		// Ensure canvas is ready
		tree.notifyOnUpdate(update);
		update();
	}
	override function get(from: Int): Dynamic {
		if (from == 1) return height;
		else if (from == 2) return width;
		else return 0;
	}
#end
}
