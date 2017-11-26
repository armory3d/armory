package armory.logicnode;

import iron.object.Object;

class UnparentNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var keepTransform:Bool = inputs[2].get();
		
		if (object == null || object.parent == null) return;

		object.parent.removeChild(object, keepTransform);

		super.run();
	}
}
