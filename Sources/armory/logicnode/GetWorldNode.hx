package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;

class GetWorldNode extends LogicNode {

	public var property0: String;
	
	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();
		if (object == null) {
			return null;
		}

		switch (property0) {
			case "right":
				return object.transform.world.right();
			case "look":
				return object.transform.world.look();
			case "up":
				return object.transform.world.up();
		}
		return null;
	}
}
