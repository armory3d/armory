package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class SetLocationNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var vec: Vec4 = inputs[2].get();
		var relative: Bool = inputs[3].get();

		if (object == null || vec == null) return;

		if (!relative && object.parent != null) {
			var loc = vec.clone();
			loc.sub(object.parent.transform.world.getLoc()); // Remove parent location influence

			// Convert vec to parent local space
			var dotX = loc.dot(object.parent.transform.right());
			var dotY = loc.dot(object.parent.transform.look());
			var dotZ = loc.dot(object.parent.transform.up());
			vec.set(dotX, dotY, dotZ);
		}

		object.transform.loc.setFrom(vec);
		object.transform.buildMatrix();

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.syncTransform();
		#end

		runOutput(0);
	}
}