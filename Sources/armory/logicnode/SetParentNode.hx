package armory.logicnode;

import armory.object.Object;

class SetParentNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();

		var parent:Object;
		var parentNode = cast(inputs[2].node, ObjectNode);
		var isUnparent = parentNode.objectName == "";
		if (isUnparent) parent = iron.Scene.active.root;
		else parent = inputs[2].get();
		
		if (object == null || parent == null) return;

		object.parent.children.remove(object);
		parent.addChild(object, !isUnparent); // applyInverse

		super.run();
	}
}
