package armory.logicnode;

import iron.object.Object;

class ClearParentNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var object:Object = inputs[1].get();
		var keepTransform:Bool = inputs[2].get();
		
		if (object == null || object.parent == null) return;

		object.parent.removeChild(object, keepTransform);
		iron.Scene.active.root.addChild(object, false);

		runOutput(0);
	}
}
