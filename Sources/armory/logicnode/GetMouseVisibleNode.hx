package armory.logicnode;

import iron.system.Input;

class GetMouseVisibleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var mouse = iron.system.Input.getMouse();

		if (mouse.hidden == false) return true;

		return false;
	}
}
