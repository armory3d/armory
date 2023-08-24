package armory.logicnode;

import iron.system.Input;

class GetMouseLockNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var mouse = iron.system.Input.getMouse();

		return mouse.locked;
	}
}
