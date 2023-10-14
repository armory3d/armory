package armory.logicnode;

import armory.trait.internal.CanvasScript;

class HideActiveCanvas extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_ui
			var value: Bool = inputs[1].get();
			CanvasScript.getActiveCanvas().setCanvasVisible(value);
		#end

		runOutput(0);
	}
}
