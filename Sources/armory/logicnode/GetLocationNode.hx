package armory.logicnode;

import iron.object.Object;

class GetLocationNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();

		if (object == null) return null;

		var loc = object.transform.world.getLoc();

		if (inputs.length > 1) { // Keep compatibility
			var relative: Bool = inputs[1].get();

			if (relative && object.parent != null) {
				loc.sub(object.parent.transform.world.getLoc()); // Add parent location influence

				// Convert vec to parent local space
				var dotX = vec.dot(object.parent.transform.right());
				var dotY = vec.dot(object.parent.transform.look());
				var dotZ = vec.dot(object.parent.transform.up());
				loc.set(dotX, dotY, dotZ);
			}
		}

		return loc;
	}
}
