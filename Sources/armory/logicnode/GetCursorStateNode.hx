package armory.logicnode;

import iron.system.Input;

class GetCursorStateNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var mouse = iron.system.Input.getMouse();

		return switch (from) {
			case 0:
				mouse.hidden && mouse.locked ? return true : return false;
			case 1:
				mouse.hidden;
			case 2:
				mouse.locked;
    			default: 
				null;
		}
	}
}
