package armory.logicnode;

import armory.object.Object;

class SetParentNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var parent:Object = inputs[2].get();
		
		if (object == null) return;
		if (parent == null) parent = tree.object;

		object.parent.children.remove(object);
		parent.addChild(object);

		super.run();
	}
}
