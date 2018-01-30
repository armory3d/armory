package armory.logicnode;

import iron.Scene;
import armory.trait.internal.CanvasScript;

class CanvasSetTextNode extends LogicNode {

	var canvas:CanvasScript;
	var element:String;
	var text:Dynamic;

	public function new(tree:LogicTree) {
		super(tree);
	}

	function update() {
		if (!canvas.ready) return;
		tree.removeUpdate(update);

		canvas.getElement(element).text = Std.string(text);
		super.run();
	}

	override function run() {
		element = inputs[1].get();
		text = inputs[2].get();
		canvas = Scene.active.getTrait(CanvasScript);

		tree.notifyOnUpdate(update);
		update();
	}
}
