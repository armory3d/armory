package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasSetLocationNode extends LogicNode {

	var canvas:CanvasScript;
	var element:String;
	var newX:Float;
	var newY:Float;

	public function new(tree:LogicTree) {
		super(tree);
	}

#if arm_ui
	function update() {
		if (!canvas.ready) return;
		tree.removeUpdate(update);

		canvas.getElement(element).x = newX;
		canvas.getElement(element).y = newY;
		super.run();
	}

	override function run() {
		element = inputs[1].get();
		newX = inputs[2].get();
		newY = inputs[3].get();
		canvas = Scene.active.getTrait(CanvasScript);
		if (canvas == null) canvas = Scene.active.camera.getTrait(CanvasScript);

		tree.notifyOnUpdate(update);
		update();
	}
#end
}
