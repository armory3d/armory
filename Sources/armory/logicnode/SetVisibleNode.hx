package armory.logicnode;

import iron.object.Object;

class SetVisibleNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var object:Object = inputs[1].get();
		var visible:Bool = inputs[2].get();
		
		if (object == null) return;

		object.visible = visible;

		runOutput(0);
	}
}
