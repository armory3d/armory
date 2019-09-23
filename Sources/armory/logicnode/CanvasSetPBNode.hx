package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasSetPBNode extends LogicNode {

	var canvas:CanvasScript;
	var element:String;
	var newAt:Int;
    var newMax:Int;

	public function new(tree:LogicTree) {
		super(tree);
	}

#if arm_ui
	function update() {
		if (!canvas.ready) return;
		tree.removeUpdate(update);

		canvas.getElement(element).progress_at = newAt;
        canvas.getElement(element).progress_total = newMax;

		runOutput(0);
	}

	override function run(from:Int) {
		element = inputs[1].get();
		newAt = inputs[2].get();
        newMax = inputs[3].get();
		canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);

		// Ensure canvas is ready
		tree.notifyOnUpdate(update);
		update();
	}
#end
}
