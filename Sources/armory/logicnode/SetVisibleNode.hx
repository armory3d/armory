package armory.logicnode;

import armory.object.Object;

class SetVisibleNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var visible:Bool = inputs[2].get();
		
		if (object == null) object = tree.object;

		object.visible = visible;

		super.run();
	}
}
