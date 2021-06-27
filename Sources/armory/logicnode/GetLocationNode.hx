package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;

class GetLocationNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();
		var relative: Bool = inputs[1].get();

		if (object == null) return null;

		var loc = object.transform.world.getLoc();

		if (relative && object.parent != null) {
			loc.sub(object.parent.transform.world.getLoc()); // Add parent location influence

			// Convert vec to parent local space
			var vec = new Vec4();
			vec.x = loc.dot(object.parent.transform.right());
			vec.y = loc.dot(object.parent.transform.look());
			vec.z = loc.dot(object.parent.transform.up());
			loc.setFrom(vec);
		}

		return loc;
	}
}
