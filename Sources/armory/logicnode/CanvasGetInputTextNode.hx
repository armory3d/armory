package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasGetInputTextNode extends LogicNode {

	var canvas: CanvasScript;

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	override function get(from: Int) {
		if (canvas == null) canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);
		if (canvas == null || !canvas.ready) return null;

		// This Try/Catch hacks around an issue where the handles are
		// not created yet, even though canvas.ready is true.
		try {
			return canvas.getHandle(inputs[0].get()).text;
		}
		catch (e: Dynamic) { return null; }
	}
#end
}
