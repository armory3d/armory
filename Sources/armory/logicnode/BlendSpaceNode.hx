package armory.logicnode;

import haxe.ds.Vector;

class BlendSpaceNode extends LogicNode {

	public var property0: Array<Bool>;
	var value: Dynamic;
	var index: Int;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {

		return property0;

	}
}
