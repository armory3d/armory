package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasSetAssetNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

#if arm_ui
	override function run(from: Int) {
		var element = inputs[1].get();
		var asset = Std.string(inputs[2].get());

		var canvas = CanvasScript.getActiveCanvas();
		canvas.notifyOnReady(() -> {
			var e = canvas.getElement(element);
			if (e != null) e.asset = asset;
			runOutput(0);
		});
	}
#end
}
