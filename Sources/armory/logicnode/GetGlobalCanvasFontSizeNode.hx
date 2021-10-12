package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class GetGlobalCanvasFontSizeNode extends LogicNode {

	var canvas: CanvasScript;

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	override function get(from: Int): Dynamic {
		canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);

		return canvas.getCanvasFontSize();
	}
#end
}