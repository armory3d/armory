package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasSetAssetNode extends LogicNode {

	var canvas:CanvasScript;
	var element:String;
	var asset:String;

	public function new(tree:LogicTree) {
		super(tree);
	}

#if arm_ui
	function update() {
		if (!canvas.ready) return;
		tree.removeUpdate(update);

		canvas.getElement(element).asset = asset;
		runOutput(0);
	}

	override function run(from:Int) {
		element = inputs[1].get();
		asset = Std.string(inputs[2].get());
		canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);

		// Ensure canvas is ready
		tree.notifyOnUpdate(update);
		update();
	}
#end
}
