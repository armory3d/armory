package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasSetVisibleNode extends LogicNode {

	var canvas: CanvasScript;
	var element: String;
	var visible: Bool;

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	function update() {
		if (!canvas.ready) return;
		tree.removeUpdate(update);

		var element = canvas.getElement(element);
		if (element != null) element.visible = this.visible;
		runOutput(0);
	}
	override function run(from: Int) {
		element = inputs[1].get();
		visible = inputs[2].get();
		canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);

		// Ensure canvas is ready
		tree.notifyOnUpdate(update);
		update();
	}
#end
}
