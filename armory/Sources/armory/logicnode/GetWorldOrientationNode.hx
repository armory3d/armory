package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;

class GetWorldOrientationNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();

		if (object == null) return null;

		return switch (property0) {
			case "Right": object.transform.world.right();
			case "Look": object.transform.world.look();
			case "Up": object.transform.world.up();
			default: null;
		}
	}
}
