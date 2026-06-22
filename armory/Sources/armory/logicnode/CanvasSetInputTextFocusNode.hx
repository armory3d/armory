package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasSetInputTextFocusNode extends LogicNode {

	var canvas: CanvasScript;
	var element: String;
	var focus: Bool;

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui

	function update() {
		if (!canvas.ready) return;
		tree.removeUpdate(update);

		var e = canvas.getHandle(element);
		if (e == null) return;

		canvas.setCanvasInputTextFocus(e, focus);

		runOutput(0);
	}

	override function run(from: Int) {

		element = inputs[1].get();
		focus = inputs[2].get();
		canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);

		// Ensure canvas is ready
		tree.notifyOnUpdate(update);
		update();

	}
#end
}
