package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasGetLocationNode extends LogicNode {

	var canvas:CanvasScript;
	var element:String;
	var x:Float;
	var y:Float;

	public function new(tree:LogicTree) {
		super(tree);
	}

#if arm_ui
	function update() {
		if (!canvas.ready) return;
		tree.removeUpdate(update);

		x = canvas.getElement(element).x;
        y = canvas.getElement(element).y;
		runOutput(0);
	}

	override function run(from:Int) {
		element = inputs[1].get();
		canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);

		// Ensure canvas is ready
		tree.notifyOnUpdate(update);
		update();
	}
    override function get(from:Int):Dynamic {
		if (from == 1) return x;
		else if (from == 2) return y;
		else return 0;
	}
#end
}
