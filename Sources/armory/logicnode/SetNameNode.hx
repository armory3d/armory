package armory.logicnode;

import armory.object.Object;

class SetNameNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var name:String = inputs[2].get();
		
		if (object == null) object = tree.object;

		object.name = name;

		super.run();
	}
}
