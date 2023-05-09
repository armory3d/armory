package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class SetGlobalCanvasFontSizeNode extends LogicNode {

	var canvas: CanvasScript;
	var factor: Int;

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	override function run(from: Int) {
		factor = inputs[1].get();
		canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);

		canvas.setCanvasFontSize(factor);
		runOutput(0);
	}
#end
}
