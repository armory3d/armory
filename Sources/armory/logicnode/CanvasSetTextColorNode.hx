package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;
import kha.Color;

class CanvasSetTextColorNode extends LogicNode {

	var canvas:CanvasScript;
	var element:String;
	var r:Float;
	var g:Float;
	var b:Float;
	var a:Float;

	public function new(tree:LogicTree) {
		super(tree);
	}

#if arm_ui
	function update() {
		if (!canvas.ready) return;
		tree.removeUpdate(update);

		canvas.getElement(element).color_text = Color.fromFloats(r,g,b,a);
		runOutput(0);
	}

	override function run(from:Int) {
		element = inputs[1].get();
		r = inputs[2].get();
		g = inputs[3].get();
		b = inputs[4].get();
		a = inputs[5].get();
		canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);

		// Ensure canvas is ready
		tree.notifyOnUpdate(update);
		update();
	}
#end
}
